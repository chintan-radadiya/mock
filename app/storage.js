window.Store = (() => {
  let db;
  function open() { return new Promise((resolve, reject) => {
    const req = indexedDB.open('cat-studio-v1', 1);
    req.onupgradeneeded = () => { for (const name of ['tests', 'attempts']) req.result.createObjectStore(name, { keyPath: 'id' }); };
    req.onsuccess = () => { db = req.result; resolve(); };
    req.onerror = () => reject(req.error);
  }); }
  function transaction(stores, mode, operation) { return new Promise((resolve, reject) => {
    const tx = db.transaction(stores, mode); let value;
    tx.oncomplete = () => resolve(value); tx.onerror = () => reject(tx.error); tx.onabort = () => reject(tx.error || new Error('Storage transaction aborted.'));
    value = operation(tx);
  }); }
  async function all(name) { let request; await transaction([name], 'readonly', tx => { request = tx.objectStore(name).getAll(); }); return request.result; }
  function put(name, value) { const snapshot = CAT.copy(value); return transaction([name], 'readwrite', tx => tx.objectStore(name).put(snapshot)); }
  function restore(tests, attempts) { return transaction(['tests', 'attempts'], 'readwrite', tx => { for (const t of tests) tx.objectStore('tests').put(t); for (const a of attempts) tx.objectStore('attempts').put(a); }); }
  return { open, all, put, restore };
})();
