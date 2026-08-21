// Error message extraction from API responses
/* Syntax: 
    - `export` make the function iportable from the other files 
    - `error.detail` read the "detail" property from the "error" object
    - `typeof x` operator in JavaScript is a built-in tool used to determine the data type of a value or variable
    - "==" is True where "===" is False
    - Array.isArray verify if error.detail is an Array
    - .map() transform every element of an Array into a new array containt message only with the same lenght cotain those errors message
    - (err) => err.msg is the same as lambda err: err.msg
    - .join(". ") combine the array into a string sperate by ". "
    - so essentially, if a string return the string, if an array of error object, return the message ib those those property and combine them into 
    one string with ". " sperator
*/

export function getErrorMessage(error) {
    if (typeof error.detail == "string"){
        return error.detail
    } else if (Array.isArray(error.detail)){
        return error.detail.map((err) => err.msg).join(". ");
    }
    return "An error occurred. Please try again.";
}

//show boostrap modal by ID'
/* Syntax:
    - This function is Boostrap's get or create instance method  with the modalID as parameter
    - const vs let:
        - const declare a variable that can not be assigned again
        - let declare a variable that can be assigned again
    - `boostrap.Modal.getOrCreateInstance`: our <div id="createPostModal"> is just HTML — inert markup describing what the modal looks like. 
    It has no ability to open or close itself. To control it, Bootstrap needs to create a JavaScript object that wraps that element and holds the modal's 
    behavior: .show(), .hide(), .toggle(), plus internal state like "am I currently open?" and the backdrop element. That wrapper object is the instance. 
    Roughly: the <div> is the body, the instance is the nervous system.
    - modal.show() fires Bootstrap's shown.bs.modal event which show that modal when user click it
*/

export function showModal(modalID){
    const modal = bootstrap.Modal.getOrCreateInstance(
        document.getElementById(modalID)
    );
    modal.show();
    return modal;
}


// Hide a Boostrap modal by ID

/*
- getInstance() will return modal if exist else null
- getOrCreateInstance() will turn modal if exist else create a totally new one
*/

export function hideModal(modalID){
    const modal = bootstrap.Modal.getInstance(
        document.getElementById(modalID)
    );
    if (modal) {
        modal.hide();
    }
}
