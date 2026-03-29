/* ======================================================
   LearnFlow — Script
   ====================================================== */

(() => {
    'use strict';

    // ── DOM refs ──────────────────────────────────────
    const textInput = document.getElementById('text-input');
    const btnGenerate = document.getElementById('btn-generate');
    const btnLoader = document.getElementById('btn-loader');
    const outputSection = document.getElementById('output-section');
    const playBtn = document.getElementById('play-btn');
    const iconPlay = document.getElementById('icon-play');
    const iconPause = document.getElementById('icon-pause');
    const progressBar = document.getElementById('progress-bar');
    const progress = document.getElementById('progress');
    const thumb = document.getElementById('thumb');
    const currentTimeEl = document.getElementById('current-time');
    const durationEl = document.getElementById('duration');
    const audioElement = document.getElementById('audio-element');
    const transcriptBody = document.getElementById('transcript-body');

    // Custom dropdown refs
    const dropdownLanguage = document.getElementById('dropdown-language');
    const dropdownStyle = document.getElementById('dropdown-style');

    // ── Helpers ───────────────────────────────────────
    function formatTime(s) {
        if (isNaN(s) || !isFinite(s)) return '0:00';
        const m = Math.floor(s / 60);
        const sec = Math.floor(s % 60).toString().padStart(2, '0');
        return `${m}:${sec}`;
    }

    function showToast(msg) {
        let toast = document.querySelector('.toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.className = 'toast';
            document.body.appendChild(toast);
        }
        toast.textContent = msg;
        requestAnimationFrame(() => {
            toast.classList.add('visible');
        });
        setTimeout(() => toast.classList.remove('visible'), 4000);
    }

    // ── Custom Dropdowns ──────────────────────────────
    function initDropdown(dropdownEl) {
        const trigger = dropdownEl.querySelector('.dropdown__trigger');
        const valueEl = dropdownEl.querySelector('.dropdown__value');
        const items = dropdownEl.querySelectorAll('.dropdown__item');

        // Toggle open/close
        trigger.addEventListener('click', (e) => {
            e.stopPropagation();
            // Close other dropdowns first
            document.querySelectorAll('.dropdown.open').forEach(d => {
                if (d !== dropdownEl) d.classList.remove('open');
            });
            dropdownEl.classList.toggle('open');
        });

        // Select item
        items.forEach(item => {
            item.addEventListener('click', (e) => {
                e.stopPropagation();
                const val = item.dataset.value;
                const label = item.textContent;

                // Update visual state
                items.forEach(i => i.classList.remove('active'));
                item.classList.add('active');
                valueEl.textContent = label;
                dropdownEl.dataset.value = val;

                // Close
                dropdownEl.classList.remove('open');
            });
        });
    }

    // Close dropdowns when clicking outside
    document.addEventListener('click', () => {
        document.querySelectorAll('.dropdown.open').forEach(d => d.classList.remove('open'));
    });

    // Close on Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            document.querySelectorAll('.dropdown.open').forEach(d => d.classList.remove('open'));
        }
    });

    // Init both dropdowns
    initDropdown(dropdownLanguage);
    initDropdown(dropdownStyle);

    textInput.addEventListener('input', checkGenerateEnabled);

    function checkGenerateEnabled() {
        const hasText = textInput.value.trim() !== '';
        btnGenerate.disabled = !hasText;
    }

    // ── Generate ──────────────────────────────────────
    btnGenerate.addEventListener('click', async () => {
        const textValue = textInput.value.trim();
        if (!textValue) return;

        // Read values from custom dropdowns
        const language = dropdownLanguage.dataset.value;
        const style = dropdownStyle.dataset.value;

        // UI: loading
        btnGenerate.classList.add('loading');
        btnGenerate.disabled = true;
        btnLoader.classList.remove('hidden');
        outputSection.classList.add('hidden');

        const formData = new FormData();
        formData.append('text', textValue);
        formData.append('language', language);
        formData.append('style', style);

        try {
            const res = await fetch('/upload-and-explain', {
                method: 'POST',
                body: formData,
            });

            if (!res.ok) {
                const err = await res.json().catch(() => null);
                throw new Error(err?.error || 'Something went wrong.');
            }

            const data = await res.json();

            // Set audio
            const audioBlob = base64ToBlob(data.audio, 'audio/wav');
            const audioUrl = URL.createObjectURL(audioBlob);
            audioElement.src = audioUrl;
            audioElement.load();

            // Set transcript
            transcriptBody.textContent = data.transcript;

            // Show output
            outputSection.classList.remove('hidden');

            // Clear input and disable button
            textInput.value = '';
            btnGenerate.disabled = true;

            // Reset player state
            resetPlayer();
        } catch (err) {
            showToast(err.message || 'Generation failed.');
        } finally {
            btnGenerate.classList.remove('loading');
            btnGenerate.disabled = false;
            btnLoader.classList.add('hidden');
        }
    });

    function base64ToBlob(base64, mime) {
        const byteChars = atob(base64);
        const byteArrays = [];
        for (let offset = 0; offset < byteChars.length; offset += 1024) {
            const slice = byteChars.slice(offset, offset + 1024);
            const byteNums = new Array(slice.length);
            for (let i = 0; i < slice.length; i++) byteNums[i] = slice.charCodeAt(i);
            byteArrays.push(new Uint8Array(byteNums));
        }
        return new Blob(byteArrays, { type: mime });
    }

    // ── Audio Player ──────────────────────────────────
    function resetPlayer() {
        iconPlay.classList.remove('hidden');
        iconPause.classList.add('hidden');
        progress.style.width = '0%';
        thumb.style.left = '0%';
        currentTimeEl.textContent = '0:00';
        durationEl.textContent = '0:00';
    }

    playBtn.addEventListener('click', () => {
        if (audioElement.paused) {
            audioElement.play();
            iconPlay.classList.add('hidden');
            iconPause.classList.remove('hidden');
        } else {
            audioElement.pause();
            iconPlay.classList.remove('hidden');
            iconPause.classList.add('hidden');
        }
    });

    audioElement.addEventListener('loadedmetadata', () => {
        durationEl.textContent = formatTime(audioElement.duration);
    });

    audioElement.addEventListener('timeupdate', () => {
        if (!audioElement.duration) return;
        const pct = (audioElement.currentTime / audioElement.duration) * 100;
        progress.style.width = pct + '%';
        thumb.style.left = pct + '%';
        currentTimeEl.textContent = formatTime(audioElement.currentTime);
    });

    audioElement.addEventListener('ended', () => {
        iconPlay.classList.remove('hidden');
        iconPause.classList.add('hidden');
    });

    // Click-to-seek on progress bar
    progressBar.addEventListener('click', (e) => {
        if (!audioElement.duration) return;
        const rect = progressBar.getBoundingClientRect();
        const ratio = (e.clientX - rect.left) / rect.width;
        audioElement.currentTime = ratio * audioElement.duration;
    });

    // Drag-to-seek
    let isDragging = false;
    progressBar.addEventListener('mousedown', (e) => {
        isDragging = true;
        seek(e);
    });
    document.addEventListener('mousemove', (e) => {
        if (isDragging) seek(e);
    });
    document.addEventListener('mouseup', () => {
        isDragging = false;
    });

    function seek(e) {
        if (!audioElement.duration) return;
        const rect = progressBar.getBoundingClientRect();
        let ratio = (e.clientX - rect.left) / rect.width;
        ratio = Math.max(0, Math.min(1, ratio));
        audioElement.currentTime = ratio * audioElement.duration;
    }
})();
