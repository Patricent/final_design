import { reactive } from 'vue'

const ACCESS_KEY = 'fd_access'
const REFRESH_KEY = 'fd_refresh'

export const authState = reactive({
  user: null,
})

export function getAccessToken() {
  return localStorage.getItem(ACCESS_KEY) || ''
}

export function getRefreshToken() {
  return localStorage.getItem(REFRESH_KEY) || ''
}

export function setTokens(access, refresh) {
  if (access) localStorage.setItem(ACCESS_KEY, access)
  if (refresh) localStorage.setItem(REFRESH_KEY, refresh)
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_KEY)
  localStorage.removeItem(REFRESH_KEY)
  authState.user = null
}

export function isLoggedIn() {
  return Boolean(getAccessToken())
}
