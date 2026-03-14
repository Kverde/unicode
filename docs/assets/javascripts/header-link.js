document.addEventListener("DOMContentLoaded", function () {
  // Делаем текст заголовка в шапке кликабельным (ссылкой на главную)
  var topics = document.querySelectorAll(".md-header__topic .md-ellipsis");
  topics.forEach(function (el) {
    var a = document.createElement("a");
    a.href = document.querySelector(".md-header__button.md-logo").getAttribute("href");
    a.style.color = "inherit";
    a.style.textDecoration = "none";
    a.textContent = el.textContent;
    el.textContent = "";
    el.appendChild(a);
  });
});
