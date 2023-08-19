window.onload = function () {
    const selectM = document.getElementById('js-male');
    const selectF = document.getElementById('js-female');
    selectM.addEventListener('click', foo, false);
    selectF.addEventListener('click', foo, false);
};
function foo() {
    alert('Hello World!');
}