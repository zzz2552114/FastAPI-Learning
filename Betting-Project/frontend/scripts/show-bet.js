let baseUrl = 'http://127.0.0.1:8000/predictions/'
let eventID = 'tomorrow-rain'
let question = document.getElementById('question')
let condition = document.getElementById('condition')
let userIdInput = document.getElementById('userid'); 
let amountInput = document.getElementById('amount');
let btnyes = document.getElementById('yes')
let btnno = document.getElementById('no')
btnyes.addEventListener('click', function() {
    submitBet('yes');
});
btnno.addEventListener('click', function() {
    submitBet('no');
});
placeBet();
setInterval(placeBet, 2000);
function placeBet() {
    fetch(baseUrl + eventID)
        .then(function(response) {
            if (!response.ok) {
                question.innerHTML = '<p style="color:red;">加载事件失败：' + error.message + '</p>';
                throw new Error('Network response was not ok');

            }
            return response.json();
        })
        .then(function(data) {
            question.innerHTML = data.question;
            let pool = data.pool;
            let totalBets = data.bets_count;
            let deadline = data.deadline
            condition.innerHTML = `<p>Total Bets: ${totalBets}<br>Yes Pool: ${pool.yes}, No Pool: ${pool.no}</p>`;
            condition.innerHTML += `<p>Deadline: ${deadline}</p>`;
        })
        .catch(function(error) {
            throw new Error('There has been a problem with your fetch operation: ' + error.message);
        })
}
function submitBet(option) {
    let userId = userIdInput.value;
    let amount = parseFloat(amountInput.value);
    fetch(baseUrl + eventID + '/bet', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_id: userId, option: option, amount: amount })
    })
    .then(function(response) {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(function(data) {
        placeBet();
        amountInput.value = '';
    })
    .catch(function(error) {
        console.error('Error submitting bet:', error);
    });

}
