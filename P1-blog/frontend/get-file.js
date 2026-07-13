let url = 'http://127.0.0.1:8000';
let buttonList = document.getElementById('button-list');
let showDiv = document.getElementById('show');

function postList() {
    fetch(`${url}/posts`)
        .then(function(response) {
            if(!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(function(data) {
            data = data.posts;
            buttonList.innerHTML = '';
            for(let i = 0; i < data.length; i++) {
                let postname = data[i];
                let button = document.createElement('button');
                button.textContent = '文章'+ postname;
                button.addEventListener('click', function() {
                    fetchPost(postname);
                });
                buttonList.appendChild(button);
            }
            showDiv.innerHTML = '<p>请选择一篇文章查看内容</p>';
        })
        .catch(function(error) {
            buttonList.innerHTML = '<p style="color:red;">加载文章列表失败：' + error.message + '</p>';
            console.error('Error fetching posts:', error);
        });
}
function fetchPost(postname) {
    showDiv.innerHTML = '<p>加载中...</p>';
    fetch(url + '/posts/' + postname)
        .then(function(response) {
            if(!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(function(data) {
            showDiv.innerHTML = marked.parse(data.content);
        })
        .catch(function(error) {
            showDiv.innerHTML = '<p style="color:red;">加载文章失败：' + error.message + '</p>';
            console.error('Error fetching post:', error);
        });
}
postList();
