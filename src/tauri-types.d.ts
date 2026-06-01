interface TauriFs {
  readTextFile(path: string): Promise<string>
  writeFile(path: string, content: string): Promise<void>
  readDir(path: string): Promise<Array<{ name: string; type: 'file' | 'directory' }>>
}

interface TauriDialog {
  open(options: { directory?: boolean; multiple?: boolean; filters?: Array<{ name: string; extensions: string[] }>; title?: string }): Promise<string | string[] | null>
  save(options: { filters?: Array<{ name: string; extensions: string[] }>; title?: string; defaultPath?: string }): Promise<string | null>
}

interface TauriPath {
  join(...paths: string[]): Promise<string>
  basename(path: string, suffix?: string): Promise<string>
}

interface TauriApi {
  fs: TauriFs
  dialog: TauriDialog
  path: TauriPath
}

declare global {
  interface Window {
    __TAURI__: TauriApi
  }
}