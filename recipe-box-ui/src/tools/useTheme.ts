import { ref, readonly, watchEffect } from 'vue';

interface ThemeState {
    isDarkMode: boolean;
    fontSizeScale: number;
    dyslexicFriendlyEnabled: boolean;
}

const STORAGE_KEY = "rb_theme_v1";

const isDarkMode = ref(false);
const fontSizeScale = ref(1.0);
const dyslexicFriendlyEnabled = ref(false);

const savedRaw = window.localStorage.getItem(STORAGE_KEY);
if (savedRaw) {
    try {
        const saved: ThemeState = JSON.parse(savedRaw);
        isDarkMode.value = !!saved.isDarkMode;
        fontSizeScale.value = saved.fontSizeScale || 1.0;
        dyslexicFriendlyEnabled.value = !!saved.dyslexicFriendlyEnabled;
    } catch {
    }
}

function persist() {
    const state: ThemeState = {
        isDarkMode: isDarkMode.value,
        fontSizeScale: fontSizeScale.value,
        dyslexicFriendlyEnabled: dyslexicFriendlyEnabled.value,
    };
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function applyToDocument() {
    const root = document.documentElement;
    const body = document.body;

    if (isDarkMode.value) {
        root.classList.add('theme-dark');
        root.classList.remove('theme-light');
    } else {
        root.classList.add('theme-light');
        root.classList.remove('theme-dark');
    }

    root.style.setProperty('--font-scale', String(fontSizeScale.value));

    if (dyslexicFriendlyEnabled.value) {
        body.classList.add('font-dyslexic');
    } else {
        body.classList.remove('font-dyslexic');
    }
}

watchEffect(() => {
    applyToDocument();
    persist();
})

export function useTheme() {
    function toggleDarkmode() {
        isDarkMode.value = !isDarkMode.value;
    }

    function setFontSizeScale(value: number) {
        fontSizeScale.value = value
    }

    function setDyslexicFriendly() {
        dyslexicFriendlyEnabled.value = !dyslexicFriendlyEnabled.value;
    }

    return {
        isDarkMode: readonly(isDarkMode),
        fontSizeScale: readonly(fontSizeScale),
        dyslexicFriendlyEnabled: readonly(dyslexicFriendlyEnabled),
        toggleDarkmode,
        setFontSizeScale,
        setDyslexicFriendly,
    };
}
