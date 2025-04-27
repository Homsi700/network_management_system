document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const errorAlert = document.getElementById('errorAlert');
    const togglePassword = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('password');

    // Toggle password visibility
    togglePassword.addEventListener('click', () => {
        const type = passwordInput.type === 'password' ? 'text' : 'password';
        passwordInput.type = type;
        togglePassword.querySelector('i').classList.toggle('fa-eye');
        togglePassword.querySelector('i').classList.toggle('fa-eye-slash');
    });

    // Handle form submission
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const remember = document.getElementById('remember').checked;

        try {
            const response = await fetch('/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username,
                    password,
                    remember_me: remember
                })
            });

            if (response.ok) {
                const data = await response.json();
                // Store the token
                localStorage.setItem('token', data.access_token);
                // Redirect to dashboard
                window.location.href = "/dashboard";
            } else {
                throw new Error('Invalid credentials');
            }
        } catch (error) {
            errorAlert.classList.remove('hidden');
            setTimeout(() => {
                errorAlert.classList.add('hidden');
            }, 5000);
        }
    });
});