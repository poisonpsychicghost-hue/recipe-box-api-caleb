# recipe-box-api frontend — main design doc

## 1. overview & goals
- purpose of the SPA (connect to existing recipe-box-api, portfolio piece, stepping stone to Pantry Project)
- constraints (single dev, learning Vue 3, no cookies, JWT BEarer only)

## 2. high-level architecture
- backend: `backend/` (existing Flask recipe-box-api)
- frontend: `src/` (Vue3 SPA)
- tech stack:
    - Vue 3 (script setup, composition API)
    - vue-router
    - minimal state via composables (no VueX/Pinia v1)
- core folders:
    - `src/views` — `LoginView`, `AppShellView`
    - `src/components` — `TopNav`, `FooterBar`, `RecipeCard`, `NotificationCenter`, modals
    - `src/tools` — `useAuth`, `useRecipes`, `useApiClient`, `useNotifications`, `useTheme`
    - `src/styles` — global styles, CSS variables (color, spacing, typography)

## 3. routing & navigation

### 3.1 routes
- `/login`
    - public
    - shows login form + "register" option
- `/app`
    - protected (requires in-memory auth token)
    - renders `AppShell` with internal tab navigation

### 3.2 app shell layout
- top: `TopNav`
    - left: app name / logo
    - center: tabs: `Search | Add | List | Admin (if role === 'admin') | Settings`
    - right: `username` + human-friendly `role` label (Member/Admin/Guest), theme toggle
- center: main content area
    - default: welcome text + last valid search OR random public recipe card
    - active tab view rendered here
- global overlays: 
    - `NotificationCenter` (toasts/snackbars)
    - shared modal components. (confirmations, session expired, forbidden)
- bottom: `FooterBar`
    - personal branding + Maestro College mention, release version, last updated date

## 4. auth & security model

### 4.1 backend assumptions
- JWT-based auth with `Authorization: Bearer <token>` 
- token contains `sub` (user id), `role` (guest, user, admin), 
- endpoints used:
    - `POST /auth/login` (email + password)
    - `POST /auth/register`
    - `GET /auth/me` (validate token, return user info)

### 4.2 token storage strategy
- access token:
    - stored **only in memory** inside `useAuth`
- session marker: 
    - `sessionStorage['rb_token_hash'] = hash(access_token)`
    - `sessionStorage['rb_user'] = { id, username, role }`
- design notes:
    - hashing in `sessionStorage` does **not** fully mitigate XSS
    - documented tradeoff chosing for learning & portfolio
    - full cookie-based design deferred to future version

### 4.3 login flow
- user submits login on `/login`
- `useAuth.login(email, password) :
    - calls `POST /auth/login`
    - on success:
        - set `authToken` (in-memory)
        - set `currentUser` (in-memory)
        - save `rb_token_hash` + `rb_user` in `sessionStorage`
        - set `authStatus = 'authenticated'`
        - router navigates to `/app`
    - on failure:
        - set `authStatus = 'error'`
        - set `authError = Invalid credientials'` (for UI)

### 4.4 route guarding & refresh behavior
- gloabal before guard for `/app`
    - if **no in-memory tokens**:
        - check `rb_token_hash`:
            - if missing -> redirect to `/login`
            - if present -> treat as "previous session existed", still require **maual login**
    - if token exists in memory: 
        - allow navigation to `/app`
- decision: **full page refresh always requires new login** even if `rb_token_hash` is present

### 4.5 token expiry & logout
- central 401 handling in `useApiClient`:
    - if backend returns "Token has Expired": 
        - call `useAuth.handleTokenExpired()`
- `handleTokenExpired()`:
    - clear in-memory token + user
    - clear `sessionStorage` keys
    - raise global "Session Expired" notification -> modal
    - on modal close: router redirects to `/login`
- `logout()`:
    - same clearing behavior
    - router redirects to `/login`
    - 'Logged out Succesfully' toast.

# 5. composables & services

### 5.1 useAuth (src/tools/useAuth)
- state:
    - `authToken`, `currentUser`, `authStatus`, `authError`
- methods:
    - `login(credentials)`
    - `logout()`
    - `handleTokenExpired()`
    - `getAuthHeader()` -> `{ Authorization: 'Bearer <token>'}` or `{}`
- integration:
    - used by router guards and `useApiClient`

### 5.2 useApiClient (src/tools/useApiClient)
- wraps fetch/axios
- automatically attaches auth header from `useAuth`
- centralized error handling:
    - `401` -> `useAuth.handleTokenExpired()`
    - `403`, `404`, `500` -> return normalized error objects to caller
- return consistent shape: `{ data, status, error }`

### 5.3 useRecipes (src/tools/useRecipes)
- state: 
    - `recipes`, `selectedRecipe`, `loading`, `error`
- methods: 
    - `fetchRecipes()` -> `GET /recipes`
    - `getRecipeById(id)` -> `GET /recipes/<id>` (for Search detail)
    - `searchRecipes(query)` client-side filter of `recipes` (v1)
    - `createRecipes(payload)` -> `POST /recipes`
    - `updateRecipe(id, patch)` -> `PATCH /recipes/<id>`
    - `deleteRecipe(id)` -> `DELETE /recipes/<id>`
- error mapping:
    - 403 -> "Forbidden: you do not own this recipe or are not an admin."
    - 404 -> "Recipe not found."
    - pass normalized messages into notification system

### 5.4 useNotifications (src/tools/useNotifications)
- state:
    - list of toasts/alerts
    - active modal config
- methods: 
    - `showToast({type, message})` (success/error/info)
    - `showModal({ type, title, messgae, onConfirm, onCancel })`
    - `clear()`
- integration: 
    - `useRecipes` and `useAuth` call into this for user feedback

### 5.5 useTheme (src/tools/useTheme)
- state: 
    - `isDarkMode`
    - `fontSizeScale`
    - `dyslexicFriendlyEnabled`
- methods:
    - `toggleDarkMode()`
    - `setFontSizeScale(value)`
    - `toggleDyslexicFriendly()`
- persists into `localStorage` or `sessionStorage`

## 6. views & components

### 6.1 LoginView
- login form (email, password)
- "Invalid Credentials" message area
- "Register" button -> registration form/modal

### 6.2 AppShellView
- owns: 
    - current tabe
    - top nav
    - main content panel
    - footer
    - notification center & global modals
- tabs rendered as child components
    - `SearchView`
    - `AddRecipeView`
    - `ListRecipesView`
    - `SettingsView`
    - `AdminView` (hidden if role !== "admin")

### 6.3 SearchView
- props: 
    - `useRole`, `userId`, `searchResults`, `isLoading`, `errorMessage`, `theme`, `settings`
- emits:
    - `search-submitted({query, filters})`
    - `request-edit(recipeId)`
    - `request-delete(recipeId)`
    - `clear-error`
- uses `RecipeCard` grid for results

### 6.4 AddRecipeView
- recipe creation form:
    - title, ingredients, instructions, `is_public` checkbox
    - title & ingredients with 'required' asterix & tooltip
- emits: 
    - `submit-create(payload)`
- success:
    - show "Added" toast + modal

### 6.5 ListRecipesView
- shows full recipe list from `useRecipes.recipes`
- same card grid layout as `SearchView`
- supports PATCH/DELETE via actions

### 6.6 AdminView
- MVP:
    - placeholder admin-only message
    - Secret Goof Message "Congratulations you have found the secret message, please send you regards to Old Pink at the Funny farm!"

### 6.7 SettingsView
- toggles:
    - light/dark mode
    - font-size slider
    - dyslexic-friendly font toggle

### 6.8 shared components 
- `RecipeCard`
    - layout per card spec, responsive(3/2/1 columns)
    - shows owner only if user is owner or admin (logic from props, no sensitve data in DOM)
- `TopNav`, `FooterBar`, `NotificationCenter`, `ConfirmModal`, etc. 

## 7. known limitations & v2 ideas
- security limitations:
    - token hashing in `sesssionStorage` is not a full XSS defense
    - no refresh token / no silent re-auth
- planned improvements:
    - migrate to httpOnly cookies + CSRF protection
    -  add richer search endpoints in backend
        - search by title, search by ingredients, search 'containing <search term>'
    - more granular admin tools
        - add/remove user, batch add/remove
    - accessibility improvements
