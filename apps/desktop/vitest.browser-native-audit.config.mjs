// Minimal Electron Browser regression runner, independent of React/Vite app plugins.
export default {
  test: {
    include: ['electron/workstation-browser*.test.ts', 'electron/browser-windows.test.ts'],
    environment: 'node',
    maxWorkers: 1,
    fileParallelism: false,
    testTimeout: 30000
  }
}
