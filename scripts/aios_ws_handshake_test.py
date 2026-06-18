#!/usr/bin/env python3
import argparse
import base64
import json
import os
import secrets
import socket
import ssl
import sys
import time
from urllib.parse import urlparse

import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

DEFAULT_API_BASE = "https://apiaios.nextbigseek.com/v2"
DEFAULT_PUBLIC_KEY_B64 = (
    "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCwD+6NnSn4kmzCxIimMk06dImcgY+NaY9Ms5KEVLVjhjBbo5dkpmJ2HJdHjIwptNLFbTWTHoxT41Wo8tcVZKj2EnH2Acv+vqFL8K8UcQDqW7eebINTBFXsu8whAjtLUB83AF97xaDshiVFzfVKKq42gXG9ofAeJNp5Rn/hv0+1NQIDAQAB"
)


def pkcs7_pad(data: bytes, block_size: int = 16) -> bytes:
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len] * pad_len)


def pkcs7_unpad(data: bytes, block_size: int = 16) -> bytes:
    if not data or len(data) % block_size != 0:
        raise ValueError("invalid padded data length")
    pad_len = data[-1]
    if pad_len < 1 or pad_len > block_size:
        raise ValueError("invalid padding length")
    if data[-pad_len:] != bytes([pad_len] * pad_len):
        raise ValueError("invalid padding bytes")
    return data[:-pad_len]


def aes_ecb_encrypt(aes_key: bytes, payload: dict) -> str:
    plain = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    cipher = Cipher(algorithms.AES(aes_key), modes.ECB()).encryptor()
    encrypted = cipher.update(pkcs7_pad(plain)) + cipher.finalize()
    return base64.b64encode(encrypted).decode("ascii")


def aes_ecb_decrypt(aes_key: bytes, encrypted_b64: str) -> dict:
    encrypted = base64.b64decode(encrypted_b64)
    cipher = Cipher(algorithms.AES(aes_key), modes.ECB()).decryptor()
    plain = cipher.update(encrypted) + cipher.finalize()
    unpadded = pkcs7_unpad(plain)
    return json.loads(unpadded.decode("utf-8"))


def rsa_encrypt_aes_key(public_key_b64: str, aes_key: bytes) -> str:
    der = base64.b64decode(public_key_b64)
    public_key = serialization.load_der_public_key(der)
    encrypted = public_key.encrypt(aes_key, asym_padding.PKCS1v15())
    return base64.b64encode(encrypted).decode("ascii")


def encrypted_post(
    session: requests.Session,
    url: str,
    payload: dict,
    public_key_b64: str,
    timeout: float,
    api_key: str = "",
) -> dict:
    aes_key = secrets.token_bytes(16)
    encrypted_key = rsa_encrypt_aes_key(public_key_b64, aes_key)
    encrypted_body = aes_ecb_encrypt(aes_key, payload)

    headers = {
        "Authorization": f"Bearer {encrypted_key}",
        "X-Encryption-Data": json.dumps({"key": encrypted_key}, separators=(",", ":")),
        "Content-Type": "application/json",
    }
    if api_key:
        headers["X-API-Key"] = api_key

    resp = session.post(url, data=encrypted_body, headers=headers, timeout=timeout)
    raw = resp.text.strip()
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}: {raw[:300]}")

    # Some environments may return plaintext JSON.
    try:
        return aes_ecb_decrypt(aes_key, raw)
    except Exception:
        return json.loads(raw)


def recv_exact(sock: socket.socket, n: int) -> bytes:
    chunks = []
    got = 0
    while got < n:
        chunk = sock.recv(n - got)
        if not chunk:
            raise RuntimeError("socket closed while reading")
        chunks.append(chunk)
        got += len(chunk)
    return b"".join(chunks)


def read_ws_text_frame(sock: socket.socket) -> str:
    hdr = recv_exact(sock, 2)
    b1, b2 = hdr[0], hdr[1]
    opcode = b1 & 0x0F
    masked = (b2 & 0x80) != 0
    length = b2 & 0x7F

    if length == 126:
        length = int.from_bytes(recv_exact(sock, 2), "big")
    elif length == 127:
        length = int.from_bytes(recv_exact(sock, 8), "big")

    mask_key = recv_exact(sock, 4) if masked else b""
    payload = recv_exact(sock, length) if length else b""

    if masked:
        payload = bytes(b ^ mask_key[i % 4] for i, b in enumerate(payload))

    if opcode == 0x1:
        return payload.decode("utf-8", errors="replace")
    if opcode == 0x8:
        raise RuntimeError("websocket closed by server")
    return f"<non-text opcode={opcode} len={len(payload)}>"


def websocket_handshake(url: str, token: str, device_id: str, bot_id: str, timeout: float) -> tuple[str, str]:
    parsed = urlparse(url)
    if parsed.scheme not in ("ws", "wss"):
        raise RuntimeError(f"unsupported websocket scheme: {parsed.scheme}")

    host = parsed.hostname
    if not host:
        raise RuntimeError("missing host in websocket url")

    port = parsed.port or (443 if parsed.scheme == "wss" else 80)
    path = parsed.path or "/"
    if parsed.query:
        path += f"?{parsed.query}"

    sock = socket.create_connection((host, port), timeout=timeout)
    if parsed.scheme == "wss":
        ctx = ssl.create_default_context()
        sock = ctx.wrap_socket(sock, server_hostname=host)
    sock.settimeout(timeout)

    sec_key = base64.b64encode(secrets.token_bytes(16)).decode("ascii")
    req = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {sec_key}\r\n"
        "Sec-WebSocket-Version: 13\r\n"
        f"Authorization: Bearer {token}\r\n"
        f"X-Device-Id: {device_id}\r\n"
        "X-AIOS-Version: 3.0\r\n"
        f"X-Bot-ID: {bot_id}\r\n"
        "\r\n"
    )

    sock.sendall(req.encode("utf-8"))

    header_bytes = b""
    while b"\r\n\r\n" not in header_bytes:
        chunk = sock.recv(4096)
        if not chunk:
            raise RuntimeError("connection closed during handshake")
        header_bytes += chunk

    header_raw, remainder = header_bytes.split(b"\r\n\r\n", 1)
    header_text = header_raw.decode("iso-8859-1", errors="replace")
    status_line = header_text.split("\r\n", 1)[0]
    if " 101 " not in status_line:
        raise RuntimeError(f"handshake failed: {status_line}\n{header_text}")

    # If first frame bytes are already in buffer, prepend through a tiny wrapper.
    if remainder:
        class PreloadedSocket:
            def __init__(self, first: bytes, real: socket.socket):
                self.first = first
                self.real = real
            def recv(self, n: int) -> bytes:
                if self.first:
                    out = self.first[:n]
                    self.first = self.first[n:]
                    return out
                return self.real.recv(n)
            def settimeout(self, t):
                self.real.settimeout(t)
        wrapper = PreloadedSocket(remainder, sock)
        first_frame = read_ws_text_frame(wrapper)  # type: ignore[arg-type]
    else:
        first_frame = read_ws_text_frame(sock)

    try:
        sock.close()
    except Exception:
        pass

    return status_line, first_frame


def main() -> int:
    parser = argparse.ArgumentParser(description="AIOS register/auth/websocket auto handshake test")
    parser.add_argument("--api-base", default=os.getenv("AIOS_API_BASE", DEFAULT_API_BASE))
    parser.add_argument("--public-key", default=os.getenv("AIOS_PUBLIC_KEY", DEFAULT_PUBLIC_KEY_B64))
    parser.add_argument("--api-key", default=os.getenv("AIOS_API_KEY", ""))
    parser.add_argument("--ws-url", default=os.getenv("AIOS_WS_URL", ""))
    parser.add_argument("--token", default=os.getenv("AIOS_TOKEN", ""))
    parser.add_argument("--device-id", default=os.getenv("AIOS_DEVICE_ID", ""))
    parser.add_argument("--bot-id", default=os.getenv("AIOS_BOT_ID", ""))
    parser.add_argument("--sn-prefix", default="test_sn_codex")
    parser.add_argument("--timeout", type=float, default=15.0)
    args = parser.parse_args()

    # Direct handshake mode: skip register/auth and validate websocket readiness directly.
    if args.ws_url and args.token and args.device_id and args.bot_id:
        print("[direct] websocket handshake + first frame")
        status_line, first_frame = websocket_handshake(
            args.ws_url,
            args.token,
            args.device_id,
            args.bot_id,
            args.timeout,
        )
        print(f"handshake status: {status_line}")
        print(f"first frame: {first_frame}")
        try:
            frame_json = json.loads(first_frame)
            if frame_json.get("event_type") != "session.connected":
                raise RuntimeError(f"unexpected first event: {frame_json}")
        except json.JSONDecodeError:
            raise RuntimeError(f"first frame is not JSON: {first_frame}")
        print("RESULT: PASS")
        return 0

    sn = f"{args.sn_prefix}_{int(time.time())}_{secrets.randbelow(10**6):06d}"
    session = requests.Session()

    print(f"[1/3] register: {args.api_base}/device/register")
    register_payload = {
        "device_product_id": 0,
        "tenant_user_id": 0,
        "sn": sn,
    }
    if args.api_key:
        register_payload["api_key"] = args.api_key
    register_resp = encrypted_post(
        session,
        f"{args.api_base}/device/register",
        register_payload,
        args.public_key,
        args.timeout,
        args.api_key,
    )
    if register_resp.get("code") != 200:
        raise RuntimeError(f"register failed: {register_resp}")

    device = register_resp["data"]["device"]
    access_key = device["access_key"]
    access_secret = device["access_secret"]
    print(f"register ok, device_user_id={device.get('user_id')}, sn={sn}")

    print(f"[2/3] auth: {args.api_base}/device/auth")
    auth_payload = {
        "access_key": access_key,
        "access_secret": access_secret,
        "imei": "",
        "sn": sn,
        "region": "cn",
        "language": "zh-CN",
    }
    if args.api_key:
        auth_payload["api_key"] = args.api_key

    auth_resp = None
    last_err = None
    for i in range(3):
        try:
            auth_resp = encrypted_post(
                session,
                f"{args.api_base}/device/auth",
                auth_payload,
                args.public_key,
                args.timeout,
                args.api_key,
            )
            break
        except Exception as e:
            last_err = e
            time.sleep(2 + i)
    if auth_resp is None:
        raise RuntimeError(f"auth failed after retries: {last_err}")
    if auth_resp.get("code") != 200:
        raise RuntimeError(f"auth failed: {auth_resp}")

    data = auth_resp["data"]
    token = data["user"]["token"]
    user_id = str(data["user"]["id"])
    ws_url = data["ws"]["url"]
    bot_id = data.get("profile_device", {}).get("config_agentic_id", "")
    if not bot_id:
        raise RuntimeError("auth response missing profile_device.config_agentic_id")

    print(f"auth ok, user_id={user_id}, bot_id={bot_id}, ws_url={ws_url}")

    print("[3/3] websocket handshake + first frame")
    status_line, first_frame = websocket_handshake(ws_url, token, user_id, bot_id, args.timeout)
    print(f"handshake status: {status_line}")
    print(f"first frame: {first_frame}")

    try:
        frame_json = json.loads(first_frame)
        if frame_json.get("event_type") != "session.connected":
            raise RuntimeError(f"unexpected first event: {frame_json}")
    except json.JSONDecodeError:
        raise RuntimeError(f"first frame is not JSON: {first_frame}")

    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"RESULT: FAIL - {exc}", file=sys.stderr)
        raise
