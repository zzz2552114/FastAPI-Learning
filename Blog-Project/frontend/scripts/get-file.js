let url = 'http://127.0.0.1:8000';
let buttonList = document.getElementById('button-list');
let relatedDiv = document.getElementById('related');
let showDiv = document.getElementById('content');
let latest = document.getElementById('latest');

function postList() {
    fetch(`${url}/api/v1/posts`)
        .then(function(response) {
            if(!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(function(data) {
            data = data.items;
            buttonList.innerHTML = '';
            for(let i = 0; i < data.length; i++) {
                let postid = data[i].id;
                let button = document.createElement('button');
                button.textContent = '文章'+ postid;
                button.addEventListener('click', function() {
                    fetchPost(postid);
                });
                buttonList.appendChild(button);
            }
            showDiv.innerHTML = '<p>请选择一篇文章查看内容</p>';
        })
        .catch(function(error) {
            buttonList.innerHTML = '<p>加载文章列表失败：' + error.message + '</p>';
            console.error('Error fetching posts:', error);
        });
}
function fetchPost(postid) {
    showDiv.innerHTML = '<p>加载中...</p>';
    fetch(`${url}/api/v1/posts/${postid}`)
        .then(function(response) {
            if(!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(function(data) {
            fetch(`${url}/api/v1/posts/${postid}/related`)
                .then(function(response) {
                    if(!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(function(relatedData) {
                    if(!relatedData || !Array.isArray(relatedData)) {
                        relatedDiv.innerHTML = `<p>该作者无其他文章</p>`;
                        return;
                    }
                    relatedDiv.innerHTML = '<p>该作者相关文章：</p>';
                    for(let i = 0; i < relatedData.length; i++) {
                        let relatedPostId = relatedData[i].id;
                        let relatedButton = document.createElement('button');
                        relatedButton.textContent = '文章' + relatedPostId;
                        relatedButton.addEventListener('click', function() {
                            fetchPost(relatedPostId);
                        });
                        relatedDiv.appendChild(relatedButton);
                    }
                })
                .catch(function(error) {
                    relatedDiv.innerHTML = '<p>加载相关文章失败：' + error.message + '</p>';
                    console.error('Error fetching related posts:', error);
                });
            showDiv.innerHTML = `<p>标题：${data.title}<br>作者：${data.author}<\p>`+ marked.parse(data.content);
        })
        .catch(function(error) {
            showDiv.innerHTML = '<p>加载文章失败：' + error.message + '</p>';
            console.error('Error fetching post:', error);
        });
}
postList();

function fetchLatestPosts() {
    showDiv.innerHTML = '<p>加载中...</p>';
    fetch(`${url}/api/v1/posts/latest`)
        .then(function(response) {
            if(!response.ok) {
                showDiv.innerHTML = '<p>加载最新文章失败：' + error.message + '</p>';
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(function(data) {
            fetchPost(data);
        })
        .catch(function(error) {
            showDiv.innerHTML = '<p>加载最新文章失败：' + error.message + '</p>';
            console.error('Error fetching latest post:', error);
        });
}
latest.addEventListener('click', fetchLatestPosts);
