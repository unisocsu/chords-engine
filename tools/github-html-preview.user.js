// ==UserScript==
// @name         GitHub.io Local HTML Loader
// @namespace    chords-engine-windows
// @version      2.0.0
// @description  Downloads a GitHub Pages index.html and opens it locally.
// @match        https://*.github.io/*
// @match        http://*.github.io/*
// @match        https://github.com/*/*/blob/*/*.html
// @match        https://github.com/*/*/blob/*/*.htm
// @grant        GM_xmlhttpRequest
// @connect      api.github.com
// @connect      raw.githubusercontent.com
// ==/UserScript==

(function () {
  'use strict';

  function request(url, done, fail) {
    GM_xmlhttpRequest({
      method: 'GET',
      url: url,
      headers: { Accept: 'application/vnd.github+json' },
      onload: done,
      onerror: fail
    });
  }

  function decodeBase64(value) {
    const binary = atob(value.replace(/\s/g, ''));
    const bytes = Uint8Array.from(binary, c => c.charCodeAt(0));
    return new TextDecoder('utf-8').decode(bytes);
  }

  function openLocal(html) {
    const blob = new Blob([html], { type: 'text/html;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const tab = window.open(url, '_blank');

    if (!tab) {
      alert('הדפדפן חסם פתיחת טאב חדש. אפשר pop-ups עבור github.io.');
      URL.revokeObjectURL(url);
      return;
    }

    setTimeout(() => URL.revokeObjectURL(url), 60000);
  }

  function errorPage(message) {
    document.documentElement.innerHTML =
      '<body dir="rtl" style="margin:0;background:#0b1020;color:white;font:16px system-ui;padding:40px">' +
      '<h1>GitHub.io Local Loader</h1><p>' + message + '</p></body>';
  }

  function rewriteAssets(html, owner, repo, branch, filePath) {
    const directory = filePath.substring(0, filePath.lastIndexOf('/') + 1);
    const rawBase =
      'https://raw.githubusercontent.com/' + owner + '/' + repo + '/' +
      branch + '/' + directory;

    html = html.replace(/<base[^>]*>/gi, '');
    return html.replace(
      /(href|src|poster|action)=(['"])(?!https?:|data:|blob:|#|\/)([^'"]+)\2/gi,
      function (_, attr, quote, value) {
        try {
          return attr + '=' + quote + new URL(value, rawBase).href + quote;
        } catch (_) {
          return _;
        }
      }
    );
  }

  function githubPages() {
    const hostMatch = location.hostname.match(/^([^.]+)\.github\.io$/);
    if (!hostMatch) return;

    const owner = hostMatch[1];
    const parts = location.pathname.split('/').filter(Boolean);

    // For a project GitHub Pages site: owner.github.io/repository/
    const repo = parts.length ? parts[0] : owner;
    const subPath = parts.length ? parts.slice(1).join('/') : '';
    const filePath = subPath
      ? 'docs/' + subPath.replace(/\/$/, '') + '/index.html'
      : 'docs/index.html';

    const apiUrl =
      'https://api.github.com/repos/' + encodeURIComponent(owner) + '/' +
      encodeURIComponent(repo) + '/contents/' +
      filePath.split('/').map(encodeURIComponent).join('/') + '?ref=main';

    request(apiUrl, function (res) {
      if (res.status < 200 || res.status >= 300) {
        errorPage('לא הצלחתי למצוא את index.html ב־GitHub (HTTP ' + res.status + ').');
        return;
      }

      let data;
      try { data = JSON.parse(res.responseText); } catch (_) {
        errorPage('GitHub החזיר תשובה לא תקינה.');
        return;
      }

      if (!data.content) {
        errorPage('לא נמצא תוכן index.html.');
        return;
      }

      let html;
      try { html = decodeBase64(data.content); } catch (_) {
        errorPage('לא הצלחתי לפענח את index.html.');
        return;
      }

      html = rewriteAssets(html, owner, repo, 'main', filePath);
      openLocal(html);
    }, function () {
      errorPage('הבקשה ל־GitHub נכשלה.');
    });
  }

  function githubBlob() {
    const match = location.pathname.match(
      /^\/([^/]+)\/([^/]+)\/blob\/([^/]+)\/(.+\.(?:html?|HTML?))$/
    );
    if (!match) return;

    const owner = match[1];
    const repo = match[2];
    const branch = match[3];
    const filePath = match[4];

    const apiUrl =
      'https://api.github.com/repos/' + encodeURIComponent(owner) + '/' +
      encodeURIComponent(repo) + '/contents/' +
      filePath.split('/').map(encodeURIComponent).join('/') +
      '?ref=' + encodeURIComponent(branch);

    request(apiUrl, function (res) {
      if (res.status < 200 || res.status >= 300) return;

      let data;
      try { data = JSON.parse(res.responseText); } catch (_) { return; }
      if (!data.content) return;

      let html;
      try { html = decodeBase64(data.content); } catch (_) { return; }

      html = rewriteAssets(html, owner, repo, branch, filePath);
      openLocal(html);
    });
  }

  if (/\.github\.io$/.test(location.hostname)) {
    githubPages();
  } else if (location.hostname === 'github.com') {
    githubBlob();
  }
})();