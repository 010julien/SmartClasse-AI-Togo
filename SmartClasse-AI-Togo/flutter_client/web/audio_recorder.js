// Web Audio Recorder for Flutter Web
let mediaStream = null;
let mediaRecorder = null;
let audioChunks = [];

// Polyfill for older browsers
const getUserMedia =
  navigator.mediaDevices?.getUserMedia ||
  navigator.webkitGetUserMedia?.bind(navigator) ||
  navigator.mozGetUserMedia?.bind(navigator) ||
  navigator.msGetUserMedia?.bind(navigator);

window.startAudioRecording = async function () {
  try {
    audioChunks = [];

    if (!getUserMedia) {
      console.error("getUserMedia not supported");
      return false;
    }

    mediaStream = await getUserMedia({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
      },
    });

    const mimeType = MediaRecorder.isTypeSupported("audio/webm")
      ? "audio/webm"
      : "audio/wav";

    mediaRecorder = new MediaRecorder(mediaStream, { mimeType });

    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };

    mediaRecorder.start();
    console.log("Audio recording started");
    return true;
  } catch (err) {
    console.error("Error accessing microphone:", err);
    return false;
  }
};

window.stopAudioRecording = async function () {
  return new Promise((resolve) => {
    if (!mediaRecorder || mediaRecorder.state === "inactive") {
      resolve(null);
      return;
    }

    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks, { type: mediaRecorder.mimeType });
      const reader = new FileReader();
      reader.onload = () => {
        const arrayBuffer = reader.result;
        resolve(arrayBuffer);
      };
      reader.readAsArrayBuffer(audioBlob);

      // Stop all tracks
      if (mediaStream) {
        mediaStream.getTracks().forEach((track) => track.stop());
        mediaStream = null;
      }
      mediaRecorder = null;
    };

    mediaRecorder.stop();
  });
};

window.isRecordingSupported = function () {
  return (
    !!getUserMedia ||
    !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia)
  );
};
