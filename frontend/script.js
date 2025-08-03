document.getElementById('team-selection').addEventListener('submit', function(event) {
    event.preventDefault();

    const nation = document.getElementById('nation').value;
    const turnTime = document.getElementById('turn-time').value;
    const general = document.getElementById('general').value;
    const commanders = document.getElementById('commanders').value.split(',');

    const playerData = {
        nation,
        turnTime,
        general,
        commanders
    };

    fetch('/set_player_choice', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(playerData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'waiting') {
            document.getElementById('team-selection').style.display = 'none';
            document.getElementById('waiting').style.display = 'block';
        }
    })
    .catch(error => console.error('Error:', error));
});
