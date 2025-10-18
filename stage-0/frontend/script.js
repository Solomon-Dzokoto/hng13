
const timeEl = document.querySelector('[data-testid="test-user-time"]');

function updateTime(){
  const now = Date.now();
  timeEl.textContent = String(now);
}

updateTime();
setInterval(updateTime, 1000);


