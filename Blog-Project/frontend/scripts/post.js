let submitButton = document.getElementById('submit-button');
let previewButton = document.getElementById('preview-button');

submitButton.addEventListener('click', function() {
    let post_title = document.getElementById('post-title').value;
    let post_author = document.getElementById('post-author').value;
    let post_content = document.getElementById('post-content').value;

    fetch(`${url}/api/v1/posts`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ title: post_title, author: post_author, content: post_content })
    })
    .then(function(response) {
        if(!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(function(data) {
        alert('文章提交成功！文章ID：' + data.post.id);
    })
    .catch(function(error) {
        alert('提交文章失败：' + error.message);
        console.error('Error submitting post:', error);
    });
    postList(); // Refresh the post list after submission
});

previewButton.addEventListener('click', function(e) {
    e.preventDefault(); // Prevent the default form submission behavior
    let post_title = document.getElementById('post-title').value;
    let post_author = document.getElementById('post-author').value;
    let post_content = document.getElementById('post-content').value;
    fetch(`${url}/api/v1/posts/preview`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ title: post_title, author: post_author, content: post_content })
    })
    .then(function(response) {
        if(!response.ok) {
            alert('预览失败：' + response.statusText);
            return;
        }
        return response.json();
    })
    .then(function(data) {
        let lineCount = data.line_count;
        let wordCount = data.word_count;
        let readingTime = data.time;
        alert(`预览结果：\n标题：${post_title}\n作者：${post_author}\n行数：${lineCount}\n字数：${wordCount}\n预计阅读时间：${readingTime}分钟`);
    })
    .catch(function(error) {
        alert('预览失败：' + error.message);
        console.error('Error previewing post:', error);
    });
})
