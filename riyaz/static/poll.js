function getCourseName() {
    let path = window.location.pathname;
    if (!path.startsWith("/courses/")) {
        return
    }

    parts = path.split("/", 3)
    if (parts.length < 3) {
        return
    }

    let courseName = parts[2]
    return courseName
}

async function startPolling(courseName, seconds) {
    let originalVersion = await getCourseVersion(courseName)

    return new Promise(resolve => {
        setInterval(async () => {
            newVersion = await getCourseVersion(courseName)
            if (newVersion != originalVersion) {
                console.log("course updated. reloading")
                resolve(window.location.reload())
            }
        }, seconds*1000)
    })
}

async function getCourseVersion(courseName) {
    const endpoint = `/api/courses/${courseName}/version`

    const response = await fetch(endpoint)
    if (!response.ok) {
        throw(`HTTP Error ${response.status}`)
    }

    const data = await response.json()
    return data.version || null;
}

window.onload = function() {
    let courseName = getCourseName()
    startPolling(courseName, 1.0)
}

