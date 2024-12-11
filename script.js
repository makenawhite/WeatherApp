function getWeather()
{
    const apiKey = ''
    const query = document.getElementById('query').value + ". Output in a list format, And add unicode to describe the weather";
    

    if (!query)
        {
            alert('Please enter a city.')
            return;
        }
        const data = sendQuery(query);
   

       

//This function will send the user input to the model and display the response on the html page 
 function sendQuery(query) {
    fetch('http://localhost:3001/query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: query }),
    })
    .then(response => response.json())
    .then(data => {
        //display the response
        var response = data.response.replaceAll("-", "<br> -")
        console.log('Response from model:', response);
        
        const weatherInfoDiv = document.getElementById('weather-info');
        weatherInfoDiv.innerHTML = `<p>${response}</p>`;

        //convert text to speech 
        const synth = window.speechSynthesis;
        const utterThis = new SpeechSynthesisUtterance(data.response);
        utterThis.lang = 'en-US';
        synth.speak(utterThis);

        return data.response;
    })
    .catch(error => console.error('Error:', error));
}

function Clear(){
    var inputarea = document.getElementById('query');
    inputarea.value = "";
    const weatherInfoDiv = document.getElementById('weather-info');
    weatherInfoDiv.innerHTML = `<p></p>`;

}