#include "otto_emoji_display.h"

#include <esp_log.h>
#include <cstring>
#include <vector>
#include <string>

#include "assets.h"
#include "assets/lang_config.h"
#include "display/lvgl_display/emoji_collection.h"
#include "display/lvgl_display/lvgl_image.h"
#include "display/lvgl_display/lvgl_theme.h"

#define TAG "OttoEmojiDisplay"

OttoEmojiDisplay::OttoEmojiDisplay(esp_lcd_panel_io_handle_t panel_io, esp_lcd_panel_handle_t panel, int width, int height, int offset_x, int offset_y, bool mirror_x, bool mirror_y, bool swap_xy)
    : SpiLcdDisplay(panel_io, panel, width, height, offset_x, offset_y, mirror_x, mirror_y, swap_xy) {
}

OttoEmojiDisplay::~OttoEmojiDisplay() {
}

void OttoEmojiDisplay::SetupUI() {
    if (setup_ui_called_) {
        ESP_LOGW(TAG, "SetupUI() called multiple times, skipping duplicate call");
        return;
    }
    
    // Call parent SetupUI() first to create all lvgl objects
    SpiLcdDisplay::SetupUI();
    
    // Setup preview image size after UI is initialized
    {
        DisplayLockGuard lock(this);
        if (preview_image_ != nullptr) {
            lv_obj_set_size(preview_image_, width_, height_);
        }
        
        // Scale the GIF emoji image to fit the screen size
        if (emoji_image_ != nullptr) {
            int zoom_factor = (width_ * 256) / 848;
            lv_image_set_scale(emoji_image_, zoom_factor);
            lv_obj_set_size(emoji_image_, width_, height_);
            lv_obj_center(emoji_image_);
            
            if (emoji_box_ != nullptr) {
                lv_obj_set_size(emoji_box_, width_, height_);
                lv_obj_center(emoji_box_);
            }
        }
    }

    // Set default emotion after UI is initialized
    SetEmotion("staticstate");
}

void OttoEmojiDisplay::SetupPreviewImage() {
    DisplayLockGuard lock(this);
    if (preview_image_ == nullptr) {
        ESP_LOGW(TAG, "SetupPreviewImage called but preview_image_ is nullptr");
        return;
    }
    lv_obj_set_size(preview_image_, width_, height_);
}

void OttoEmojiDisplay::InitializeOttoEmojis() {
    ESP_LOGI(TAG, "Otto表情初始化将由Assets系统处理");
}

void OttoEmojiDisplay::SetEmotion(const char* emotion) {
    if (!emotion) return;
    ESP_LOGI(TAG, "SetEmotion: %s", emotion);
    SpiLcdDisplay::SetEmotion(emotion);
}

LV_FONT_DECLARE(OTTO_ICON_FONT);
void OttoEmojiDisplay::SetStatus(const char* status) {
    auto lvgl_theme = static_cast<LvglTheme*>(current_theme_);
    auto text_font = lvgl_theme->text_font()->font();
    DisplayLockGuard lock(this);
    if (!status) {
        ESP_LOGE(TAG, "SetStatus: status is nullptr");
        return;
    }

    if (strcmp(status, Lang::Strings::LISTENING) == 0) {
        lv_obj_set_style_text_font(status_label_, &OTTO_ICON_FONT, 0);
        lv_label_set_text(status_label_, "\xEF\x84\xB0");  // U+F130 麦克风图标
        lv_obj_clear_flag(status_label_, LV_OBJ_FLAG_HIDDEN);
        lv_obj_add_flag(network_label_, LV_OBJ_FLAG_HIDDEN);
        lv_obj_add_flag(battery_label_, LV_OBJ_FLAG_HIDDEN);
        return;
    } else if (strcmp(status, Lang::Strings::SPEAKING) == 0) {
        lv_obj_set_style_text_font(status_label_, &OTTO_ICON_FONT, 0);
        lv_label_set_text(status_label_, "\xEF\x80\xA8");  // U+F028 说话图标
        lv_obj_clear_flag(status_label_, LV_OBJ_FLAG_HIDDEN);
        lv_obj_add_flag(network_label_, LV_OBJ_FLAG_HIDDEN);
        lv_obj_add_flag(battery_label_, LV_OBJ_FLAG_HIDDEN);
        return;
    } else if (strcmp(status, Lang::Strings::CONNECTING) == 0) {
        lv_obj_set_style_text_font(status_label_, &OTTO_ICON_FONT, 0);
        lv_label_set_text(status_label_, "\xEF\x83\x81");  // U+F0c1 连接图标
        lv_obj_clear_flag(status_label_, LV_OBJ_FLAG_HIDDEN);
        return;
    } else if (strcmp(status, Lang::Strings::STANDBY) == 0) {
        lv_obj_set_style_text_font(status_label_, text_font, 0);
        lv_label_set_text(status_label_, "");
        lv_obj_clear_flag(status_label_, LV_OBJ_FLAG_HIDDEN);
        lv_obj_clear_flag(network_label_, LV_OBJ_FLAG_HIDDEN);
        lv_obj_clear_flag(battery_label_, LV_OBJ_FLAG_HIDDEN);
        return;
    }

    lv_obj_set_style_text_font(status_label_, text_font, 0);
    lv_label_set_text(status_label_, status);
}

void OttoEmojiDisplay::SetPreviewImage(std::unique_ptr<LvglImage> image) {
    SpiLcdDisplay::SetPreviewImage(std::move(image));
}