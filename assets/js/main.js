(() => {
  const siteHeader = document.querySelector('.site-header');
  const updateHeaderHeight = () => {
    if (!siteHeader) return;
    document.documentElement.style.setProperty('--site-header-height', `${siteHeader.getBoundingClientRect().height}px`);
  };
  if (siteHeader) {
    updateHeaderHeight();
    new ResizeObserver(updateHeaderHeight).observe(siteHeader);
  }

  const nav = document.querySelector('.greedy-nav');
  const navButton = nav?.querySelector('.nav-toggle');
  const menu = nav?.querySelector('.visible-links');

  if (nav && navButton && menu) {
    const closeMenu = () => {
      nav.classList.remove('is-open');
      navButton.classList.remove('close');
      navButton.setAttribute('aria-expanded', 'false');
      updateHeaderHeight();
    };

    navButton.addEventListener('click', () => {
      const isOpen = nav.classList.toggle('is-open');
      navButton.classList.toggle('close', isOpen);
      navButton.setAttribute('aria-expanded', String(isOpen));
    });

    menu.addEventListener('click', closeMenu);
    nav.querySelector('.masthead__brand')?.addEventListener('click', closeMenu);
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') closeMenu();
    });
  }

  const languageButton = document.getElementById('language-switch');
  const languageLabel = languageButton?.querySelector('.language-switch__label');
  const translatedElements = Array.from(document.querySelectorAll('[data-zh]'), (element) => ({
    element,
    english: element.textContent
  }));
  const updateThemeLabel = () => {
    const isChinese = document.documentElement.lang === 'zh-CN';
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    document.getElementById('theme-switch')?.setAttribute('aria-label', isChinese
      ? (isDark ? '切换到白天模式' : '切换到黑夜模式')
      : (isDark ? 'Switch to light mode' : 'Switch to dark mode'));
  };
  const setLanguage = (language) => {
    document.documentElement.lang = language;
    translatedElements.forEach(({ element, english }) => {
      element.textContent = language === 'zh-CN' ? element.dataset.zh : english;
    });
    if (languageButton) {
      const isChinese = language === 'zh-CN';
      languageLabel.textContent = isChinese ? 'English' : '中文';
      languageButton.lang = isChinese ? 'en' : 'zh-CN';
      languageButton.setAttribute('aria-label', isChinese ? 'Switch to English' : '切换到中文');
      languageButton.hidden = false;
    }
    updateThemeLabel();
  };

  setLanguage(document.documentElement.lang);
  languageButton?.addEventListener('click', () => {
    const language = document.documentElement.lang === 'zh-CN' ? 'en' : 'zh-CN';
    setLanguage(language);
    try {
      window.localStorage.setItem('site-language', language);
    } catch {}
  });

  const themeButton = document.getElementById('theme-switch');
  const themeLabel = themeButton?.querySelector('.theme-switch__label');
  if (!themeButton || !themeLabel) return;

  const THEME_KEY = 'site-theme';
  const DARK = 'dark';
  const LIGHT = 'light';

  const supportsStorage = (() => {
    try {
      const k = '__test_theme__';
      window.localStorage.setItem(k, '1');
      window.localStorage.removeItem(k);
      return true;
    } catch {
      return false;
    }
  })();

  const systemTheme = () => (window.matchMedia('(prefers-color-scheme: dark)').matches ? DARK : LIGHT);
  const readStoredTheme = () => {
    if (!supportsStorage) return null;
    const value = window.localStorage.getItem(THEME_KEY);
    return value === DARK || value === LIGHT ? value : null;
  };

  const writeTheme = (theme) => {
    if (supportsStorage) {
      window.localStorage.setItem(THEME_KEY, theme);
    }
    document.documentElement.setAttribute('data-theme', theme);
    const isDark = theme === DARK;
    themeButton.setAttribute('aria-pressed', String(isDark));
    updateThemeLabel();

    const themeColor = isDark ? '#142338' : '#004098';
    const themeMeta = document.querySelector('meta[name="theme-color"]');
    if (themeMeta) themeMeta.setAttribute('content', themeColor);
  };

  const initTheme = readStoredTheme() || systemTheme();
  writeTheme(initTheme);

  themeButton.addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === DARK ? LIGHT : DARK;
    writeTheme(next);
  });

  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
  const handleSystemThemeChange = () => {
    if (readStoredTheme() === null) {
      writeTheme(systemTheme());
    }
  };

  if (typeof mediaQuery.addEventListener === 'function') {
    mediaQuery.addEventListener('change', handleSystemThemeChange);
  } else {
    mediaQuery.addListener(handleSystemThemeChange);
  }
})();
