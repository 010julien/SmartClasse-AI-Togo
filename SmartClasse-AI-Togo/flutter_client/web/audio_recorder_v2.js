// Web Audio Recorder for Flutter Web - Fixed version
let mediaStream = null;
let mediaRecorder = null;
let audioChunks = [];

window.startAudioRecording = function () {
  return navigator.mediaDevices
    .getUserMedia({
      audio: true,
    })
    .then((stream) => {
      mediaStream = stream;
      audioChunks = [];

      const mimeType = MediaRecorder.isTypeSupported("audio/webm")
        ? "audio/webm"
        : "audio/wav";

      mediaRecorder = new MediaRecorder(mediaStream, { mimeType });

      mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };

      mediaRecorder.onerror = (event) => {
        console.error("MediaRecorder error:", event.error);
      };

      mediaRecorder.start();
      console.log("Audio recording started");
      return true;
    })
    .catch((err) => {
      console.error("Error accessing microphone:", err);
      return false;
    });
};

window.stopAudioRecording = function () {
  return new Promise((resolve) => {
    if (!mediaRecorder || mediaRecorder.state === "inactive") {
      resolve(null);
      return;
    }

    mediaRecorder.onstop = () => {
      const audioBlob = new Blob(audioChunks, { type: mediaRecorder.mimeType });
      const reader = new FileReader();
      reader.onload = () => {
        const arrayBuffer = reader.result;
        resolve(arrayBuffer);
      };
      reader.onerror = () => {
        console.error("FileReader error:", reader.error);
        resolve(null);
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
  return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
};

// Test logging
console.log("Audio recorder v2 loaded");
console.log("Recording supported:", window.isRecordingSupported());
