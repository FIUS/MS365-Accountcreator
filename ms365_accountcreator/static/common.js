function executeRequestAndProcess(request, on_success = function (data) { }, on_failure = function (message) { }) {
    let resp = null
    request()
        .then(response => {
            resp = response
            if (response.status == 204) {
                //Empty body
                return response.text();
            }
            return response.json()
        })
        .then(data => {
            let response = resp
            let content = data
            if (response.status == 204) {
                on_success(null)
            } else if (response.ok) {
                on_success(content)
            } else {
                let status = response.status
                let message = ""
                if (status == 422) {
                    if ((! "errors" in content) || (!content.errors.constructor == Object)) throw "Data format invalid"
                    for (let key in content.errors) {
                        value = content.errors[key]
                        if (!value.constructor == Object) throw "Data format invalid" //Check for dict/object
                        for (let innerkey in value) {
                            innervalue = value[innerkey]
                            if (!Array.isArray(innervalue)) throw "Data format invalid"
                            for (let i in innervalue) {
                                if (message.length > 0 && message.charAt(message.length - 1) != ' ') {
                                    message += ' '
                                }
                                message += innervalue[i]
                            }
                        }
                    }
                } else {
                    if (! "message" in content) {
                        throw "Data format invalid"
                    }
                    message = content.message
                }
                on_failure(message)
            }
        })
        .catch(() => {
            on_failure(connection_error_text)
        });
}

function postData(url = '', data = {}) {
    return fetch(url, {
        method: 'POST',
        mode: 'cors',
        cache: 'no-cache',
        headers: {
            'Content-Type': 'application/json',
            'lang': lang
        },
        body: JSON.stringify(data)
    });
}

function postDataAndProcess(url = '', data = {}, on_success = function (data) { }, on_failure = function (message) { }) {
    request = () => {return postData(url, data)}
    executeRequestAndProcess(request, on_success, on_failure)
}

function getData(url = '') {
    return fetch(url, {
        method: 'GET',
        mode: 'cors',
        cache: 'no-cache',
        headers: {
            'lang': lang
        }
    });
}

function getDataAndProcess(url = '', on_success = function (data) { }, on_failure = function (message) { }) {
    request = () => {return getData(url)}
    executeRequestAndProcess(request, on_success, on_failure)
}

function updateData(url = '', data = {}) {
    return fetch(url, {
        method: 'PUT',
        mode: 'cors',
        cache: 'no-cache',
        headers: {
            'Content-Type': 'application/json',
            'lang': lang
        },
        body: JSON.stringify(data)
    });
}

function updateDataAndProcess(url = '', data = {}, on_success = function (data) { }, on_failure = function (message) { }) {
    request = () => {return updateData(url, data)}
    executeRequestAndProcess(request, on_success, on_failure)
}

function deleteData(url = '') {
    return fetch(url, {
        method: 'DELETE',
        mode: 'cors',
        cache: 'no-cache',
        headers: {
            'lang': lang
        }
    });
}

function deleteDataAndProcess(url = '', on_success = function (data) { }, on_failure = function (message) { }) {
    request = () => {return deleteData(url)}
    executeRequestAndProcess(request, on_success, on_failure)
}

function showToast(message) {
    if(typeof toastClearingTimeout !== 'undefined' && toastClearingTimeout != null) {
        clearTimeout(toastClearingTimeout)
    }
    let snackbar = document.getElementById("snackbar");
    snackbar.innerHTML = message;
    snackbar.className = "show";
    toastClearingTimeout = setTimeout(function(){ snackbar.className = "hide" }, 3000);
}

function copyToClipboard(string) {
    navigator.clipboard.writeText(string).then(function() {
        showToast("Copied");
      }, function(err) {
        console.error('Async: Could not copy text: ', err);
      });
}
