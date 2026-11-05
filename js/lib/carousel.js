(function () {
  document.querySelectorAll('.carousel').forEach(function (carousel) {
    var track = carousel.querySelector('.carousel__track');
    if (!track) return;
    var prev = carousel.querySelector('.carousel__btn--prev');
    var next = carousel.querySelector('.carousel__btn--next');
    var scrollByCard = function (dir) {
      var card = track.querySelector('.carousel__item');
      var amount = card ? card.getBoundingClientRect().width + 16 : 300;
      track.scrollBy({ left: dir * amount, behavior: 'smooth' });
    };
    if (prev) prev.addEventListener('click', function () { scrollByCard(-1); });
    if (next) next.addEventListener('click', function () { scrollByCard(1); });
  });

  var dialog = document.createElement('dialog');
  dialog.className = 'gallery-lightbox';
  var img = document.createElement('img');
  dialog.appendChild(img);
  dialog.addEventListener('click', function () { dialog.close(); });
  document.body.appendChild(dialog);

  document.querySelectorAll('.gallery img').forEach(function (thumb) {
    thumb.addEventListener('click', function () {
      img.src = thumb.currentSrc || thumb.src;
      dialog.showModal();
    });
  });
})();
