document.getElementById('registerForm').addEventListener('submit', function (e) {
    // 客户端验证用户名
    const username = document.getElementById('username').value.trim();
    const messageElement = document.getElementById('message');

    if (username === "") {
        messageElement.textContent = "用户名不能为空";
        e.preventDefault();
    }
});