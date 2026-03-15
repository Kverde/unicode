document$.subscribe(() => {
  // pymdownx.highlight ставит класс языка на div.highlight, а не на code
  document.querySelectorAll('.language-javascript.highlight, .language-js.highlight').forEach(highlightDiv => {
    if (highlightDiv.dataset.runJsAttached) return;
    highlightDiv.dataset.runJsAttached = '1';

    const codeEl = highlightDiv.querySelector('code');
    if (!codeEl) return;

    // Кнопка «▶ Запустить»
    const btn = document.createElement('button');
    btn.className = 'run-js-btn';
    btn.textContent = '▶ Запустить';

    // Блок для вывода
    const output = document.createElement('pre');
    output.className = 'run-js-output';
    output.hidden = true;

    highlightDiv.before(btn);
    highlightDiv.after(output);

    btn.addEventListener('click', () => {
      const code = codeEl.textContent;
      const lines = [];

      const orig = {
        log:   console.log,
        warn:  console.warn,
        error: console.error,
      };

      const capture = (...args) =>
        lines.push(
          args.map(a =>
            a !== null && typeof a === 'object'
              ? JSON.stringify(a)
              : String(a)
          ).join(' ')
        );

      console.log   = capture;
      console.warn  = (...a) => capture('[warn]', ...a);
      console.error = (...a) => capture('[error]', ...a);

      try {
        // eslint-disable-next-line no-new-func
        new Function(code)();
      } catch (e) {
        lines.push(`Ошибка: ${e.message}`);
      } finally {
        Object.assign(console, orig);
      }

      output.textContent = lines.length ? lines.join('\n') : '(нет вывода)';
      output.hidden = false;
    });
  });
});
