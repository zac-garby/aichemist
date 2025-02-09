var cameraCanvas: HTMLCanvasElement
var cameraContext: CanvasRenderingContext2D
var video: HTMLVideoElement

var paused: boolean = false

function startCamera() {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({
            video: { facingMode: "environment" }
        }).then(function(stream) {
            video = document.createElement('video')
            video.srcObject = stream
            video.playsInline = true
            video.play()

            cameraCanvas = document.getElementById('cam') as HTMLCanvasElement
            cameraContext = cameraCanvas.getContext('2d')!

            const dpr = window.devicePixelRatio || 1.0
            cameraCanvas.width = cameraCanvas.clientWidth * dpr
            cameraCanvas.height = cameraCanvas.clientHeight * dpr
            cameraContext.scale(dpr, dpr)

            video.addEventListener("canplay", drawFrame)
        }).catch(function(error) {
            console.error("An error occurred: ", error)
        })
    }
}

function drawFrame() {
    if (!paused) {
        const aspectRatio = video.videoWidth / video.videoHeight
        const targetRatio = cameraCanvas.clientWidth / cameraCanvas.clientHeight

        let sx = 0
        let sy = 0
        let sw = video.videoWidth
        let sh = video.videoHeight

        if (aspectRatio > targetRatio) {
            sw = video.videoHeight * targetRatio
            sx = (video.videoWidth - sw) / 2
        } else if (aspectRatio < targetRatio) {
            sh = video.videoWidth / targetRatio
            sy = (video.videoHeight - sh) / 2
        }

        cameraCanvas.width = cameraCanvas.width
        cameraContext.drawImage(
            video,
            sx, sy, sw, sh, 0, 0,
            cameraCanvas.width, cameraCanvas.height
        )
    }

    requestAnimationFrame(drawFrame)
}

function takePhoto() {
    console.log("taking photo")
    const data = cameraCanvas.toDataURL("image/png")
    const base64 = data.split(",")[1]
    console.log("photo taken. size:", base64.length)

    setWaitMessage("The Gods Above are pondering your request...", 100000)
    paused = true

    fetch("/api/upload-image", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            image: base64,
        })
    }).then(r => r.json()).then(j => {
        if (j.message) {
            showMessage(j.message)
        }
    }).then(fetchState).finally(() => {
        clearTimeout(moveWaitTimeoutID)
        paused = false
    })
}
