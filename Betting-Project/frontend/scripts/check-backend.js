check_button = document.getElementById('check-backend')
message = document.getElementById('message')

function checkBackend() {
    message.innerHTML = '正在连接……'
    fetch('http://127.0.0.1:8000/health')
        .then(function (response) {
            if (!response.ok) {
                message.innerHTML = '网络连接失败：' + response.status + ' ' + response.statusText;
                throw new Error('Network response was not ok');
            }
            message.innerHTML = '网络连接成功！';
            return response.json();
        })
        .then(function (data) {
            if (data.project === 'Betting') {
                message.innerHTML += `<br>后端连接成功，项目名称：${data.project}`;
            } else {
                message.innerHTML += '<br>后端返回数据不符合预期';
            }
        })
        .catch(function (error) {
            message.innerHTML = '<p>连接失败：' + error.message + '</p>';
            console.error('Error checking backend:', error);
        });
}
check_button.addEventListener('click', checkBackend);
