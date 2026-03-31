(function () {
  'use strict';

  const form = document.getElementById('shortenForm');
  const result = document.getElementById('result');
  const submitBtn = document.getElementById('submitBtn');
  const input = document.getElementById('targetUrl');

  function showSuccess(shortUrl) {
    result.className = 'success';
    result.innerHTML = [
      '<div style="text-align: center; width: 100%;">',
      '  <div class="short-url">',
      '    <strong>Короткая ссылка:</strong><br>',
      '    <a href="' + shortUrl + '" target="_blank">' + shortUrl + '</a>',
      '  </div>',
      '  <button class="copy-btn" data-copy="' + shortUrl + '">Копировать ссылку</button>',
      '</div>'
    ].join('');

    const copyBtn = result.querySelector('.copy-btn');
    if (copyBtn) {
      copyBtn.addEventListener('click', function () {
        copyToClipboard(copyBtn.getAttribute('data-copy'), copyBtn);
      });
    }
  }

  function showError(message) {
    result.className = 'error';
    result.innerHTML = '<strong>Ошибка:</strong> ' + message;
  }

  function copyToClipboard(text, buttonEl) {
    navigator.clipboard.writeText(text).then(function () {
      var originalText = buttonEl.textContent;
      buttonEl.textContent = 'Скопировано';
      setTimeout(function () {
        buttonEl.textContent = originalText;
      }, 2000);
    }).catch(function () {
      alert('Не удалось скопировать. Скопируйте вручную: ' + text);
    });
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var url = input.value.trim();

    if (!url) {
      showError('Пожалуйста, введите URL');
      return;
    }

    var fullUrl = url;
    if (url.indexOf('http://') !== 0 && url.indexOf('https://') !== 0) {
      fullUrl = 'https://' + url;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = 'Создание...';
    result.innerHTML = '';

    fetch('/shorten', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target: fullUrl })
    })
      .then(function (response) {
        return response.json().then(function (data) {
          return { ok: response.ok, data: data };
        });
      })
      .then(function (_ref) {
        var ok = _ref.ok;
        var data = _ref.data;

        if (!ok) {
          showError(data.detail || 'Произошла ошибка');
          return;
        }
        showSuccess(data.short_url);
        input.value = '';
      })
      .catch(function () {
        showError('Ошибка сети. Проверьте подключение к интернету.');
      })
      .finally(function () {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Создать короткую ссылку';
      });
  });
})();
