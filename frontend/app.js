// frontend/app.js
const api = (path, opts={}) => {
  const headers = opts.headers || {};
  return fetch('/api'+path, {...opts, headers}).then(async r => {
    const text = await r.text();
    try { return JSON.parse(text); } catch(e) { return text; }
  });
};

let token = null;

async function refresh(){
  const list = await api('/elections');
  const el = document.getElementById('elections');
  el.innerHTML = '';
  if(!Array.isArray(list)) return;
  list.forEach(e=>{
    const div = document.createElement('div');
    div.innerHTML = `<h3>${e.title}</h3><p>${e.description||''}</p>`;
    e.options.forEach(o=>{
      const b = document.createElement('button');
      b.textContent = `${o.text} (${o.votes})`;
      b.onclick = async ()=>{
        if(!token){alert('login first'); return}
        const res = await fetch('/api/vote',{
          method:'POST',
          headers:{'Content-Type':'application/json','Authorization':'Bearer '+token},
          body:JSON.stringify({election_id:e.id, option_id:o.id})
        });
        const data = await res.json();
        alert(data.msg||JSON.stringify(data));
        refresh();
      };
      div.appendChild(b);
    });
    el.appendChild(div);
  });
}

document.getElementById('register').onclick = async ()=>{
  const u = document.getElementById('username').value;
  const p = document.getElementById('password').value;
  const res = await fetch('/api/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:u,password:p})});
  alert((await res.json()).msg||'');
};

document.getElementById('login').onclick = async ()=>{
  const u = document.getElementById('username').value;
  const p = document.getElementById('password').value;
  const res = await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:u,password:p})});
  const data = await res.json();
  if(data.access_token){token = data.access_token; alert('logged in');
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      if(payload.identity && payload.identity.is_admin) document.getElementById('admin').style.display='block';
    } catch(e){}
  } else alert(data.msg||JSON.stringify(data));
};

document.getElementById('create_election').onclick = async ()=>{
  const t = document.getElementById('e_title').value;
  const d = document.getElementById('e_desc').value;
  const opts = document.getElementById('e_options').value.split(',').map(s=>s.trim()).filter(Boolean);
  const res = await fetch('/api/elections',{method:'POST',headers:{'Content-Type':'application/json','Authorization':'Bearer '+token},body:JSON.stringify({title:t,description:d,options:opts})});
  alert((await res.json()).msg||'');
  refresh();
};

refresh();
