const msgerForm = get(".msger-inputarea");
const msgerInput = get(".msger-input");
const msgerChat = get(".msger-chat");

document.getElementById("initial_time").textContent = formatDate(new Date());

// Icons made by Freepik from www.flaticon.com
const BOT_IMG = '/static/images/upaj_logo_new.png';
const PERSON_IMG = '/static/images/asset_4_2x_8_1.png';
const BOT_NAME = "Upaj Mitra";
const PERSON_NAME = "User";
const apiURL = "https://umapiuat.igrow.ag"

const msgInput = document.getElementById('msgInput');
const sendBtn = document.getElementById('sendBtn');

msgInput.addEventListener('keypress', event => {
    if(event.key === "Enter") {
        event.preventDefault();
        sendBtn.click();
    }
})

msgerForm.addEventListener("submit", event => {
  event.preventDefault();
  const msgText = msgerInput.value;
  if (!msgText) return;
  console.log('calling post API')
  $.ajax({
	  url: apiURL+"/send",
	  type: "POST",
	  dataType: "json",
	  contentType: "application/json; charset=utf-8",
	  data: JSON.stringify({
        	query: msgText,
    		}),
	  beforeSend: function() {
        	$('#loader').removeClass('hidden')
    		},
	  success: function (result) {
       	botResponse(result)
    		},
    	  error: function (err) {
		botResponse(err)
    	  },
	  complete: function(){
        $('#loader').addClass('hidden')
    }});
  appendIncomingMessage(PERSON_NAME, PERSON_IMG, "right", msgText);
  //botResponse(obj);
 msgerInput.value = "";

//botResponse();
});


function appendIncomingMessage(name, img, side, text) {
  //   Simple solution for small apps
  const msgHTML = `
    <div class="msg ${side}-msg">
      <div class="msg-img" style="background-image: url(${img})"></div>

      <div class="msg-bubble">
        <div class="msg-info">
          <div class="msg-info-name">${name}</div>
          <div class="msg-info-time">${formatDate(new Date())}</div>
        </div>

        <div class="msg-text">${text}</div>
      </div>
    </div>
  `;

  msgerChat.insertAdjacentHTML("beforeend", msgHTML);
  msgerChat.scrollTop += 500;
}

function appendMessage(name, img, side, text, audio, videos) {
  //   Simple solution for small apps
  var msgHTML = `
    <div class="msg ${side}-msg">
      <div class="msg-img" style="background-image: url(${img});background-color: #1c3f2f;"></div>

      <div class="msg-bubble">
        <div class="msg-info">
          <div class="msg-info-name">${name}</div>
          <div class="msg-info-time">${formatDate(new Date())}</div>
        </div>

        <div class="msg-text">${text}</div>
        <br>`

        if (typeof videos !== 'undefined' && videos.length > 1) {
          let videoHTML = `
        <iframe width="210" height="200" src="${videos[0]}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
        <iframe width="210" height="200" src="${videos[1]}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
        <iframe width="210" height="200" src="${videos[2]}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
        <br><br>`
        msgHTML = msgHTML + videoHTML
      }

      
      // if (typeof image !== 'undefined' && image.length > 0) {
      //   let imageHTML = `
      //     <a href="${image[0]['Image_1']}" target="_blank"><img src="${image[0]['Image_1']}" style="width:128px;height:128px;"></a>
      //     <a href="${image[1]['Image_2']}" target="_blank"><img src="${image[1]['Image_2']}" style="width:128px;height:128px;"></a>
      //     <a href="${image[2]['Image_3']}" target="_blank"><img src="${image[2]['Image_3']}" style="width:128px;height:128px;"></a>
      //     <a href="${image[3]['Image_4']}" target="_blank"><img src="${image[3]['Image_4']}" style="width:128px;height:128px;"></a>
      //     <a href="${image[4]['Image_5']}" target="_blank"><img src="${image[4]['Image_5']}" style="width:128px;height:128px;"></a>
      //     <br><br>`
      //           msgHTML = msgHTML + imageHTML
      //   }
      
        if (typeof audio !== 'undefined' && audio.length > 0) {
          let audioHTML = `
                  <audio controls>
                  <source src="data:audio/wav;base64,${audio}" type="audio/wav"/>
                  </audio>
                  </div>
            </div>` 
            msgHTML = msgHTML + audioHTML
      }   
  ;
  msgerChat.insertAdjacentHTML("beforeend", msgHTML);
  msgerChat.scrollTop += 500;
}

function botResponse(resp) {
  resp = resp['result'][0]
  data = resp['data']
  audio = resp['audio']
  videos = resp['videos']
  appendMessage(BOT_NAME, BOT_IMG, "left", data, audio, videos);
}

function botResponseforVoice(resp) {
  data = resp['data']
  original_text = resp['original_text']
  // image = resp['images']
  audio = resp['audio']
  videos = resp['videos']
  appendIncomingMessage(PERSON_NAME, PERSON_IMG, "right", original_text);
  appendMessage(BOT_NAME, BOT_IMG, "left", data, audio, videos);
}

// Utils
function get(selector, root = document) {
  return root.querySelector(selector);
}

function formatDate(date) {
  const h = "0" + date.getHours();
  const m = "0" + date.getMinutes();

  return `${h.slice(-2)}:${m.slice(-2)}`;
}

function random(min, max) {
  return Math.floor(Math.random() * (max - min) + min);
}

class VoiceRecorder {
	constructor() {
		if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
			console.log("getUserMedia supported")
		} else {
			console.log("getUserMedia is not supported on your browser!")
		}

		this.mediaRecorder
		this.stream
		this.chunks = []
		this.isRecording = false

		this.recorderRef = document.querySelector("#recorder")
		this.playerRef = document.querySelector("#player")
		this.startRef = document.querySelector("#start")
		this.stopRef = document.querySelector("#stop")
		
		this.startRef.onclick = this.startRecording.bind(this)
		this.stopRef.onclick = this.stopRecording.bind(this)

		this.constraints = {
			audio: true,
			video: false
		}
		
	}

	handleSuccess(stream) {
		this.stream = stream
		this.stream.oninactive = () => {
			console.log("Stream ended!")
		};
		this.recorderRef.srcObject = this.stream
		this.mediaRecorder = new MediaRecorder(this.stream)
		console.log(this.mediaRecorder)
		this.mediaRecorder.ondataavailable = this.onMediaRecorderDataAvailable.bind(this)
		this.mediaRecorder.onstop = this.onMediaRecorderStop.bind(this)
		this.recorderRef.play()
		this.mediaRecorder.start()
	}

	handleError(error) {
		console.log("navigator.getUserMedia error: ", error)
	}
	
	onMediaRecorderDataAvailable(e) { this.chunks.push(e.data) }
	
	onMediaRecorderStop(e) { 
			const blob = new Blob(this.chunks, { 'type': 'audio/wav; codecs=MS_PCM' })
			this.chunks = []
			this.stream = null     
      let formData = new FormData();
      formData.append('data', blob)
      
      $.ajax({
        url: apiURL+"/sendVoice",
        type: "POST",
        processData: false,
        contentType: false,
        data: formData,
        beforeSend: function() {
              $('#loader').removeClass('hidden')
            },
        success: function (result) {
          botResponseforVoice(result)
            },
            error: function (err) {
        botResponse(err)
            },
        complete: function(){
            $('#loader').addClass('hidden')
        }});
	}

	startRecording() {
		if (this.isRecording) return
		this.isRecording = true
		this.startRef.innerHTML = 'Recording...'
		// this.playerRef.src = ''
		navigator.mediaDevices
			.getUserMedia(this.constraints)
			.then(this.handleSuccess.bind(this))
			.catch(this.handleError.bind(this))
	}
	
	stopRecording() {
		if (!this.isRecording) return
		this.isRecording = false
		this.startRef.innerHTML = 'Record'
		this.recorderRef.pause()
		this.mediaRecorder.stop()
	}
	
}

window.voiceRecorder = new VoiceRecorder()


