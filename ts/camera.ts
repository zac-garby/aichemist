var canvas: HTMLCanvasElement
var context: CanvasRenderingContext2D
var video: HTMLVideoElement

function startCamera() {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true }).then(function(stream) {
            video = document.createElement('video')
            video.srcObject = stream
            video.play()

            canvas = document.getElementById('cam') as HTMLCanvasElement
            context = canvas.getContext('2d') as CanvasRenderingContext2D

            const dpr = window.devicePixelRatio || 1.0
            canvas.width = canvas.clientWidth * dpr
            canvas.height = canvas.clientHeight * dpr
            context.scale(dpr, dpr)

            video.addEventListener("canplay", drawFrame)
            canvas.addEventListener("click", takePhoto)
        }).catch(function(error) {
            console.error("An error occurred: ", error)
        })
    }
}

function drawFrame() {
    const aspectRatio = video.videoWidth / video.videoHeight
    const targetRatio = canvas.clientWidth / canvas.clientHeight

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

    canvas.width = canvas.width
    context.drawImage(
        video,
        sx, sy, sw, sh, 0, 0,
        canvas.width, canvas.height
    )

    requestAnimationFrame(drawFrame)
}

function takePhoto() {
    console.log("taking photo")

    const data = canvas.toDataURL("image/png")
    const base64 = data.split(",")[1]

    fetch("/api/upload-image", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            image: base64,
        })
    })
}
