/* ==========================================================================
   VoterInfo — core/static/core/js/script.js
   Handles: dark mode toggle, navbar live search (AJAX), global loading
   spinner on form submits / links, and toast auto-dismiss.
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function () {

  /* ---------------- Dark Mode Toggle ---------------- */
  const root = document.documentElement;
  const toggleBtn = document.getElementById('darkModeToggle');
  const savedTheme = window.localStorage ? localStorage.getItem('voterinfo-theme') : null;

  if (savedTheme) {
    root.setAttribute('data-bs-theme', savedTheme);
    updateToggleIcon(savedTheme);
  }

  if (toggleBtn) {
    toggleBtn.addEventListener('click', function () {
      const current = root.getAttribute('data-bs-theme') === 'dark' ? 'dark' : 'light';
      const next = current === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-bs-theme', next);
      updateToggleIcon(next);
      try { localStorage.setItem('voterinfo-theme', next); } catch (e) { /* ignore */ }
    });
  }

  function updateToggleIcon(theme) {
    if (!toggleBtn) return;
    const icon = toggleBtn.querySelector('i');
    if (!icon) return;
    icon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill';
  }

  /* ---------------- Toast auto-dismiss ---------------- */
  document.querySelectorAll('.toast').forEach(function (toastEl) {
    setTimeout(function () {
      toastEl.classList.remove('show');
    }, 5000);
  });

  /* ---------------- Global spinner on form submit ---------------- */
  const spinner = document.getElementById('globalSpinner');
  document.querySelectorAll('form').forEach(function (form) {
    form.addEventListener('submit', function () {
      if (form.id === 'navSearchForm') return; // search handled separately
      if (spinner) spinner.classList.remove('d-none');
    });
  });

  /* ---------------- Navbar Live Search (booth by PIN / area) ---------------- */
  const searchInput = document.getElementById('navSearchInput');
  const resultsBox = document.getElementById('searchResultsDropdown');
  let debounceTimer = null;

  if (searchInput && resultsBox) {
    searchInput.addEventListener('input', function () {
      const query = searchInput.value.trim();
      clearTimeout(debounceTimer);

      if (query.length < 2) {
        resultsBox.classList.add('d-none');
        resultsBox.innerHTML = '';
        return;
      }

      debounceTimer = setTimeout(function () {
        fetch('/search/?q=' + encodeURIComponent(query))
          .then(function (res) { return res.json(); })
          .then(function (data) {
            renderSearchResults(data.results || []);
          })
          .catch(function () {
            resultsBox.classList.add('d-none');
          });
      }, 300);
    });

    document.addEventListener('click', function (e) {
      if (!resultsBox.contains(e.target) && e.target !== searchInput) {
        resultsBox.classList.add('d-none');
      }
    });
  }

  function renderSearchResults(results) {
    if (!results.length) {
      resultsBox.innerHTML = '<div class="search-item text-muted">No booths found.</div>';
      resultsBox.classList.remove('d-none');
      return;
    }
    resultsBox.innerHTML = results.map(function (r) {
      return (
        '<div class="search-item">' +
        '<strong>' + escapeHtml(r.booth_name) + '</strong> (' + escapeHtml(r.booth_number) + ')<br>' +
        '<span class="text-muted">' + escapeHtml(r.address) + ' — PIN: ' + escapeHtml(r.pin_code) + '</span>' +
        '</div>'
      );
    }).join('');
    resultsBox.classList.remove('d-none');
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }
});
