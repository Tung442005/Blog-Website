//auth.js is frontend only, and it's not tied to login.html specifically; 
// it's a shared browser module that every page imports. 
//Cache" = keep a copy of an answer you already fetched, so you don't fetch it again.
let currentUser = null;
let fetchPromise = null;

export async function getCurrentUser() {
  // user cache: is the currentUser variable store the copy of `/me` answer so no more request need to be called
  // if we have the cached user --> return that user immediately
  if (currentUser) {
    return currentUser;
  }

  // Return in-progress fetch to prevent duplicate API calls
  if (fetchPromise) {
    return fetchPromise;
  }
  //store the token in localStorage to prevent token being wiped off  due inpersistent storage
  const token = localStorage.getItem("access_token");
  if (!token) {
    return null;
  }

  fetchPromise = (async () => {
    //Fetch the backend route Because the frontend doesn't know who the user is — it only holds an opaque token string request by client side. 
    // The backend is the only party that can turn that string into a user then return the strintified JSON response and render it .
    // Also since it call backend, it can automatically validte the token since we define in auth.py
    try {
      const response = await fetch("/api/users/me", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        currentUser = await response.json();
        return currentUser;
      }
      // if the token expire or invalid, we gonna remove the token from the localStorage
      localStorage.removeItem("access_token");
      return null;
    } catch (error) {
      console.error("Error fetching current user:", error);
      return null;
    } finally {
      fetchPromise = null;
    }
  })();

  return fetchPromise;
}

//Helper Functions

export function logout() {
  // remove token from localStorage
  localStorage.removeItem("access_token");
  // clear the user cache(credential)
  currentUser = null;
  //the redirect doubles as a clean slate, 
  //since a fresh page load re-runs getCurrentUser() which now finds no token → renders logged-ouy
  window.location.href = "/";
}

export function getToken() {
  return localStorage.getItem("access_token");
}

export function setToken(token) {
  localStorage.setItem("access_token", token);
}

export function clearUserCache() {
  currentUser = null;
}