mod audio;

use audio::capture::{list_input_devices, start_capture, stop_capture, AudioCaptureState, AudioDeviceInfo};
use parking_lot::Mutex;
use tauri::{
    menu::{Menu, MenuItem},
    tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent},
    AppHandle, Emitter, Manager, RunEvent,
};
use tauri_plugin_global_shortcut::{Code, GlobalShortcutExt, Modifiers, Shortcut};

struct CaptureState(Mutex<AudioCaptureState>);

#[tauri::command]
fn list_audio_input_devices() -> Result<Vec<AudioDeviceInfo>, String> {
    list_input_devices()
}

#[tauri::command]
fn start_audio_capture(
    app: AppHandle,
    state: tauri::State<'_, CaptureState>,
    device_index: Option<u32>,
) -> Result<(), String> {
    start_capture(app, &mut state.0.lock(), device_index)
}

#[tauri::command]
fn stop_audio_capture(state: tauri::State<'_, CaptureState>) -> Result<(), String> {
    stop_capture(&mut state.0.lock())
}

fn build_tray(app: &AppHandle) -> tauri::Result<()> {
    let show_i = MenuItem::with_id(app, "show", "Show Voragon", true, None::<&str>)?;
    let quit_i = MenuItem::with_id(app, "quit", "Quit", true, None::<&str>)?;
    let menu = Menu::with_items(app, &[&show_i, &quit_i])?;

    let _tray = TrayIconBuilder::new()
        .icon(app.default_window_icon().unwrap().clone())
        .menu(&menu)
        .show_menu_on_left_click(true)
        .on_menu_event(|app, event| match event.id.as_ref() {
            "show" => {
                if let Some(window) = app.get_webview_window("main") {
                    let _ = window.show();
                    let _ = window.set_focus();
                }
            }
            "quit" => {
                app.exit(0);
            }
            _ => {}
        })
        .on_tray_icon_event(|tray, event| {
            if let TrayIconEvent::Click {
                button: MouseButton::Left,
                button_state: MouseButtonState::Up,
                ..
            } = event
            {
                let app = tray.app_handle();
                if let Some(window) = app.get_webview_window("main") {
                    let _ = window.show();
                    let _ = window.set_focus();
                }
            }
        })
        .build(app)?;
    Ok(())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_store::Builder::default().build())
        .plugin(
            tauri_plugin_global_shortcut::Builder::new()
                .with_handler(|app, _shortcut, _event| {
                    let _ = app.emit("transcription-toggle", ());
                })
                .build(),
        )
        .manage(CaptureState(Mutex::new(AudioCaptureState::default())))
        .invoke_handler(tauri::generate_handler![
            list_audio_input_devices,
            start_audio_capture,
            stop_audio_capture
        ])
        .setup(|app| {
            build_tray(app.handle())?;
            let shortcut = Shortcut::new(Some(Modifiers::SUPER | Modifiers::SHIFT), Code::KeyT);
            app.global_shortcut().register(shortcut)?;
            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("error while running tauri application")
        .run(|app_handle, event| {
            if let RunEvent::Exit = event {
                if let Some(state) = app_handle.try_state::<CaptureState>() {
                    let _ = stop_capture(&mut state.0.lock());
                }
            }
        });
}
