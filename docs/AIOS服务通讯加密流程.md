# AIOS服务通讯加密流程

这是一个非常典型的混合加密方案（RSA + AES-ECB），这种设计能很好地兼顾安全性（非对称加密保护密钥）与性能（对称加密处理大数据）。

## 技术规格

### 加密算法

- **RSA**: PKCS1 v1.5 加密/解密，SHA256 签名
- **AES**: ECB 模式，PKCS7 填充
- **密钥长度**: AES-128 (16字节)，RSA-2048/4096
- **编码**: Base64 编码所有加密数据

### 密钥管理

- 服务端存放私钥（`APP_PRIVATE_KEY` 环境变量，Base64编码的一行字符串）
- 前端存放公钥（`APP_PUBLIC_KEY` 环境变量，Base64编码的一行字符串）
- AES 密钥为每次请求随机生成

### 密钥格式说明

- **私钥格式**: Base64编码的DER格式，无PEM头尾标记
- **公钥格式**: Base64编码的DER格式，无PEM头尾标记
- **示例**: `MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...`

## 详细流程

### 请求流程（前端 → 服务端）

1. **前端准备阶段**
   - 生成 16 字节随机 AES 密钥 `aesKey`
   - 使用 RSA 公钥加密 `aesKey` 得到 `encryptedAesKey`
   - 使用 `aesKey` 加密请求 JSON 数据得到 `encryptedBody`

2. **请求构造**
   - 设置请求头：`Authorization: Bearer {encryptedAesKey}`
   - 设置请求头：`Content-Type: application/json`
   - 设置请求体：`encryptedBody`
   - 发起 POST 请求

3. **服务端处理阶段**
   - 从 `X-Encryption-Data` 头提取 JSON 数据并解析得到 `encryptedAesKey`
   - 使用 RSA 私钥解密得到原始 `aesKey`
   - 使用 `aesKey` 解密请求体得到原始 JSON 数据
   - 处理业务逻辑，生成响应 JSON

### 响应流程（服务端 → 前端）

4. **服务端响应构造**
   - 使用相同的 `aesKey` 加密响应 JSON 得到 `encryptedResponse`
   - 对 `aesKey` 进行 RSA 签名得到 `signature`
   - 设置响应头：`X-Seek-Signature: {signature}`
   - 返回加密的响应体

5. **前端验证与解密**
   - 使用 RSA 公钥验证 `X-Seek-Signature` 签名
   - 使用 `aesKey` 解密响应体得到最终数据

## 错误处理

### 服务端错误码

- `403 Forbidden`: X-Encryption-Data 头格式错误、JSON解析失败或 RSA 解密失败
- `400 Bad Request`: 请求体读取失败或 AES 解密失败
- `500 Internal Server Error`: 加密或签名过程出错

### 前端错误处理

- 检查响应状态码
- 验证签名有效性
- 处理解密失败情况

## 安全考虑

### 优势

1. **前向安全性**: 每次请求使用不同的 AES 密钥
2. **密钥保护**: AES 密钥通过 RSA 加密传输
3. **完整性验证**: 响应通过签名验证
4. **防重放**: 随机 AES 密钥防止重放攻击

### 注意事项

1. **ECB 模式**: 对于结构化数据可能存在模式泄露风险
2. **密钥长度**: 确保 AES 密钥为 16/24/32 字节
3. **时间窗口**: 考虑请求超时和密钥有效期

## 前端加密伪代码

```javascript
class AIOSEncryptionClient {
  constructor(publicKey) {
    this.publicKey = publicKey;
  }

  // 生成随机AES密钥
  generateAESKey() {
    return crypto.getRandomValues(new Uint8Array(16));
  }

  // RSA加密AES密钥
  async encryptAESKey(aesKey) {
    const encrypted = await window.crypto.subtle.encrypt(
      { name: "RSA-OAEP" },
      this.publicKey,
      aesKey,
    );
    return btoa(String.fromCharCode(...new Uint8Array(encrypted)));
  }

  // AES-ECB加密数据
  async encryptData(aesKey, data) {
    const encoder = new TextEncoder();
    const encodedData = encoder.encode(JSON.stringify(data));

    // PKCS7填充
    const blockSize = 16;
    const padding = blockSize - (encodedData.length % blockSize);
    const paddedData = new Uint8Array(encodedData.length + padding);
    paddedData.set(encodedData);
    paddedData.fill(padding, encodedData.length);

    const encrypted = await window.crypto.subtle.encrypt(
      { name: "AES-ECB" },
      aesKey,
      paddedData,
    );
    return btoa(String.fromCharCode(...new Uint8Array(encrypted)));
  }

  // 发送加密请求
  async sendEncryptedRequest(url, data) {
    const aesKey = await this.generateAESKey();
    const encryptedAesKey = await this.encryptAESKey(aesKey);
    const encryptedBody = await this.encryptData(aesKey, data);

    const response = await fetch(url, {
      method: "POST",
      headers: {
        "X-Encryption-Data": JSON.stringify({ key: encryptedAesKey }),
        "Content-Type": "application/json",
      },
      body: encryptedBody,
    });

    // 验证签名并解密响应
    return await this.handleEncryptedResponse(response, aesKey);
  }

  // 处理加密响应
  async handleEncryptedResponse(response, aesKey) {
    const signature = response.headers.get("X-Seek-Signature");
    const encryptedData = await response.text();

    // 验证签名
    const isValid = await this.verifySignature(aesKey, signature);
    if (!isValid) {
      throw new Error("Invalid response signature");
    }

    // 解密数据
    return await this.decryptData(aesKey, encryptedData);
  }
}
```

## 多语言样例伪代码

### JavaScript (Node.js)

```javascript
const crypto = require("crypto");

class AIOSEncryption {
  constructor(publicKeyBase64) {
    // 将Base64字符串转换为Buffer，然后创建公钥
    const publicKeyDer = Buffer.from(publicKeyBase64, "base64");
    this.publicKey = crypto.createPublicKey({
      key: publicKeyDer,
      format: "der",
      type: "pkcs1",
    });
  }

  // 生成AES密钥
  generateAESKey() {
    return crypto.randomBytes(16);
  }

  // RSA加密
  rsaEncrypt(plaintext) {
    return crypto
      .publicEncrypt(
        {
          key: this.publicKey,
          padding: crypto.constants.RSA_PKCS1_PADDING,
        },
        plaintext,
      )
      .toString("base64");
  }

  // AES-ECB加密
  aesEncryptECB(key, data) {
    const cipher = crypto.createCipher("aes-128-ecb", key);
    let encrypted = cipher.update(data, "utf8", "base64");
    encrypted += cipher.final("base64");
    return encrypted;
  }
}
```

### Go

```go
package main

import (
    "crypto/rand"
    "crypto/rsa"
    "crypto/x509"
    "encoding/base64"
    "fmt"
)

type AIOSClient struct {
    PublicKey *rsa.PublicKey
}

func NewAIOSClient(publicKeyBase64 string) (*AIOSClient, error) {
    // 解码Base64字符串得到DER格式的公钥
    publicKeyDer, err := base64.StdEncoding.DecodeString(publicKeyBase64)
    if err != nil {
        return nil, fmt.Errorf("failed to decode base64 public key: %v", err)
    }

    // 解析DER格式的公钥
    pub, err := x509.ParsePKCS1PublicKey(publicKeyDer)
    if err != nil {
        // 尝试PKIX格式
        pkixPub, err := x509.ParsePKIXPublicKey(publicKeyDer)
        if err != nil {
            return nil, fmt.Errorf("failed to parse public key: %v", err)
        }

        rsaPub, ok := pkixPub.(*rsa.PublicKey)
        if !ok {
            return nil, fmt.Errorf("not an RSA public key")
        }
        pub = rsaPub
    }

    return &AIOSClient{PublicKey: pub}, nil
}

func (c *AIOSClient) GenerateAESKey() ([]byte, error) {
    key := make([]byte, 16)
    _, err := rand.Read(key)
    return key, err
}

func (c *AIOSClient) EncryptAESKey(aesKey []byte) (string, error) {
    encrypted, err := rsa.EncryptPKCS1v15(rand.Reader, c.PublicKey, aesKey)
    if err != nil {
        return "", err
    }
    return base64.StdEncoding.EncodeToString(encrypted), nil
}
```

### Java

```java
import javax.crypto.Cipher;
import java.security.KeyFactory;
import java.security.PublicKey;
import java.security.spec.X509EncodedKeySpec;
import java.util.Base64;

public class AIOSEncryption {
    private PublicKey publicKey;

    public AIOSEncryption(String publicKeyBase64) throws Exception {
        // 直接解码Base64字符串得到DER格式的公钥
        byte[] keyBytes = Base64.getDecoder().decode(publicKeyBase64);
        X509EncodedKeySpec keySpec = new X509EncodedKeySpec(keyBytes);
        KeyFactory keyFactory = KeyFactory.getInstance("RSA");
        this.publicKey = keyFactory.generatePublic(keySpec);
    }

    public byte[] generateAESKey() {
        SecureRandom random = new SecureRandom();
        byte[] key = new byte[16];
        random.nextBytes(key);
        return key;
    }

    public String encryptAESKey(byte[] aesKey) throws Exception {
        Cipher cipher = Cipher.getInstance("RSA/ECB/PKCS1Padding");
        cipher.init(Cipher.ENCRYPT_MODE, publicKey);
        byte[] encrypted = cipher.doFinal(aesKey);
        return Base64.getEncoder().encodeToString(encrypted);
    }
}
```

### Python

```python
import base64
import os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

class AIOSEncryption:
    def __init__(self, public_key_base64):
        # 解码Base64字符串得到DER格式的公钥
        public_key_der = base64.b64decode(public_key_base64)
        self.public_key = serialization.load_der_public_key(public_key_der)

    def generate_aes_key(self):
        return os.urandom(16)

    def encrypt_aes_key(self, aes_key):
        encrypted = self.public_key.encrypt(
            aes_key,
            padding.PKCS1v15()
        )
        return base64.b64encode(encrypted).decode()

    def aes_encrypt_ecb(self, key, data):
        # 注意：Python cryptography 库不直接支持 ECB 模式
        # 需要手动实现或使用其他库
        cipher = Cipher(algorithms.AES(key), modes.ECB())
        encryptor = cipher.encryptor()

        # PKCS7 填充
        block_size = 16
        padding_length = block_size - (len(data) % block_size)
        padded_data = data + bytes([padding_length] * padding_length)

        encrypted = encryptor.update(padded_data) + encryptor.final()
        return base64.b64encode(encrypted).decode()
```

### C/C++ (OpenSSL)

```c
#include <openssl/rsa.h>
#include <openssl/bio.h>
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <string.h>

class AIOSEncryption {
private:
    RSA* public_key;

public:
    AIOSEncryption(const char* public_key_base64) {
        // 解码Base64字符串得到DER格式的公钥
        BIO* bio_mem = BIO_new_mem_buf(public_key_base64, -1);
        BIO* bio_b64 = BIO_new(BIO_f_base64());
        BIO_push(bio_b64, bio_mem);

        unsigned char der_buffer[2048];
        int der_len = BIO_read(bio_b64, der_buffer, sizeof(der_buffer));

        // 从DER格式解析公钥
        const unsigned char* p = der_buffer;
        public_key = d2i_RSA_PUBKEY(NULL, &p, der_len);

        BIO_free_all(bio_b64);
    }

    ~AIOSEncryption() {
        RSA_free(public_key);
    }

    bool generate_aes_key(unsigned char* aes_key) {
        return RAND_bytes(aes_key, 16) == 1;
    }

    std::string encrypt_aes_key(const unsigned char* aes_key) {
        unsigned char encrypted[256];
        int encrypted_len = RSA_public_encrypt(
            16, aes_key, encrypted, public_key, RSA_PKCS1_PADDING
        );

        if (encrypted_len == -1) {
            return "";
        }

        return base64_encode(encrypted, encrypted_len);
    }
};
```

## 测试与验证

### 单元测试要点

1. **密钥生成**: 验证AES密钥随机性和长度
2. **加解密一致性**: 加密后解密应得到原始数据
3. **错误处理**: 测试无效密钥、错误格式等边界情况
4. **性能测试**: 评估加解密性能，特别是大数据量场景

### 集成测试

```javascript
// 示例集成测试
async function testEncryptionFlow() {
  const client = new AIOSEncryptionClient(publicKey);
  const testData = { message: "Hello, AIOS!" };

  try {
    const response = await client.sendEncryptedRequest(
      "https://api.example.com/endpoint",
      testData,
    );
    console.log("Test passed:", response);
  } catch (error) {
    console.error("Test failed:", error);
  }
}
```

## 部署配置

### 环境变量

```bash
# 服务端（Base64编码的一行字符串）
APP_PRIVATE_KEY="MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC..."

# 前端（Base64编码的一行字符串）
APP_PUBLIC_KEY="MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA..."
```

### 密钥生成

```bash
# 生成RSA密钥对
openssl genrsa -out private.pem 2048
openssl rsa -in private.pem -pubout -out public.pem

# 转换为Base64一行字符串格式（移除PEM头尾和换行符）
# 私钥
cat private.pem | grep -v "PRIVATE KEY" | tr -d '\n' > private_base64.txt

# 公钥
cat public.pem | grep -v "PUBLIC KEY" | tr -d '\n' > public_base64.txt
```

此文档提供了完整的加密流程说明、多语言实现示例和部署指南，可作为开发参考。
