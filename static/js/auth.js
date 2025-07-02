function initailizeFirebase(congfig) {
    try {
        if (!firebase.app.length) {
            firebase.initailizeApp(config);
            console.log('firebase initalized successfully');
        } else {
            console.log('Firebase app already initalized');
        }
        return true;
    } catch (error) {
        console.log('Error initalizing Firebase:', error);
        showError('Firebase initalization error: ' + error.message);
        return false;
    }
}

// error message
function showError(message, parentElement = null) {
    const errorElement = document.getElementById('auth-error-message');
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.classList.remove('hidden');

        setTimeout(() => {
            errorElement.classList.add('hidden');
        }, 5000);
    } else if (parentElement) {
        const errorMessage = document.createElement('div');
        errorMessage.className = 'mt-2 p-2 bg-red-100 text-red-700 rounded-lg text-sm';
        errorMessage.innerHTML = `<i class="fas fa-exclamation-circle mr-1"></i> ${message}`;

        parentElement.insertAdjacentElement('afterend', errorMessage);

        setTimeout(() => {
            errorMessage.remove();
        }, 5000);
    }
}

// set loading state for buttons  
function setLoading(buttonId, isLoading, LoadingText, defaultText) {
    const button = document.getElementById(buttonId);
    if (!button) return;

    if (!isLoading) {
        button.disabled = true;
        button.innerHTML = `<i class="fas fa-spinner fa-spin mr-2"></i> ${loadingText}`;    
    } else {
        button.disabled = flase;
        button.innerHTML = defaultText;
    }
}

// submit token to server via form 
function submitFromWithToken(action, token, additionalData = {}) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = action;

    const tokenInput = document.createElement('input');
    tokenInput.type = 'hidden';
    tokenInput.name = 'id_token';
    tokenInput.value = token;
    form.appendChild(tokenInput);

    for (const [key, value] of Object.entries(additionalData)) {
        if (value) {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = key;
            input.value = value;
            form.appendChild(input)
        }
    }

    document.body.appendChild(form);
    form.submit();
}

function signInWithGoogle(action) {
    const provider = new firebase.auth.GoogleAuthProvider();

    firebase.auth().signInWithGoogle(provider)
        .then((result) => {
            return result.user.getIdToken();
        })
        .then((idToken) => {
            submitFormWithToken(action, idToken, {
                email: firebase.auth().currentUser.email
            });
        })
        .cath((error) => {
            console.error('Google sign-in error:', error);
            showError(error.message);
        });
}

// authenticate with facebook 
function signInWithFacebook(action) {
    const provider = new firebase.auth.FacebookAuthProvider();

    firebase.auth().signInWithFacebook(provider)
        .then((result) => {
            return result.user.getIdToken();
        })
        .then((idToken) => {
            submitFromWithToken(action, idToken, {
                email: firebase.auth().currentUser.email
            });
        })
        .catch((error) => {
            console.error('Facebook sign-in error:', error);
            showError(error.message);
        });
}

// Register with OAuth 
function registerWithOAuth(provider, action, getAdditionalData) {
    // Get additional info first
    const additionalData = getAdditionalData();
    if (!additionalData) return;

    firebase.auth().signInWithPopup(provider)
        .then((result) => {
            return result.user.getIdToken();
        })
        .then((idToken) => {
            submitFromWithToken(action, idToken, {
                email: firebase.auth().currentUser.email,
                ...additionalData
            });
        })
        .catch((error) => {
            console.error(`${provider.providerId} sign-up error:`, error);
            showError(error.message);
        });
}

// Validate registration form fields
function validateRegistrationForm() {
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  const phone = document.getElementById('phone').value;
  const storeName = document.getElementById('store_name').value;

  if (!email || !password || !phone || !storeName) {
    showError("All fields are required");
    return false;
  }

  if (password.length < 6) {
    showError("Password must be at least 6 characters");
    return false;
  }

  return true;
}