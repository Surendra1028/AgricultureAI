import {useEffect,useState} from 'react';
import {Sprout,Leaf,CloudSun,FlaskConical,TrendingUp,Upload,AlertCircle} from 'lucide-react';
import api from './api';
import { languages, translate, translateCropResult } from './i18n';
const nav=[['home','Overview'],['crop','Crop recommendation'],['disease','Disease detection'],['fert','Fertilizer guidance'],['yield','Yield prediction'],['weather','Weather insights'],['history','Prediction history']];
const box='rounded-2xl border border-emerald-100 bg-white p-5 shadow-sm';
function App(){
 const [language,setLanguage]=useState('en');
 const [authReady,setAuthReady]=useState(false),[user,setUser]=useState(null);
 const [authMode,setAuthMode]=useState('login'),[authForm,setAuthForm]=useState({full_name:'',email:'',password:''}),[authBusy,setAuthBusy]=useState(false),[authError,setAuthError]=useState(''),[authSuccess,setAuthSuccess]=useState('');
 const t=(value)=>translate(value,language);
 const [page,setPage]=useState('home'),[status,setStatus]=useState('Checking'),[result,setResult]=useState(null),[notice,setNotice]=useState(''),[history,setHistory]=useState([]),[busy,setBusy]=useState(false);
 const [crop,setCrop]=useState({N:90,P:42,K:43,temperature:20.8,humidity:82,ph:6.5,rainfall:202});
 const [cropMode,setCropMode]=useState('basic');
 const [farmer,setFarmer]=useState({location:'Nellore, Andhra Pradesh',land_acres:2,season:'Kharif',irrigation:'Canal',soil_type:"Don't know",previous_crop:''});
 const [weatherLocation,setWeatherLocation]=useState('Nellore, Andhra Pradesh');
 const [fert,setFert]=useState({crop:'Rice',nitrogen:35,phosphorus:25,potassium:30});
 const [yieldData,setYieldData]=useState({crop:'Rice',area_hectares:1.01,rainfall_mm:900,average_temperature_c:26,fertilizer_kg_per_hectare:100,year:2026});
 const [landUnit,setLandUnit]=useState('acres');
 const [landVal,setLandVal]=useState(2.5);
 const [weather,setWeather]=useState(null);
 const CROP_PRESETS = [
   { name: 'Rice', crop: 'Rice', rain: 950, temp: 26, fert: 110 },
   { name: 'Wheat', crop: 'Wheat', rain: 450, temp: 18, fert: 120 },
   { name: 'Maize', crop: 'Maize', rain: 650, temp: 24, fert: 110 },
   { name: 'Cotton', crop: 'Cotton', rain: 700, temp: 27, fert: 100 },
   { name: 'Sugarcane', crop: 'Sugarcane', rain: 1400, temp: 28, fert: 200 },
   { name: 'Groundnut', crop: 'Groundnut', rain: 550, temp: 25, fert: 60 },
   { name: 'Tomato', crop: 'Tomato', rain: 600, temp: 23, fert: 120 },
   { name: 'Potato', crop: 'Potato', rain: 500, temp: 19, fert: 140 }
 ];
 const handleLandChange = (val, unit = landUnit) => {
   setLandVal(val);
   const num = parseFloat(val);
   if (!isNaN(num) && num > 0) {
     const ha = unit === 'acres' ? +(num / 2.471).toFixed(2) : +num.toFixed(2);
     setYieldData(prev => ({ ...prev, area_hectares: ha }));
   }
 };
 const handleUnitSwitch = (newUnit) => {
   if (newUnit === landUnit) return;
   setLandUnit(newUnit);
   const num = parseFloat(landVal);
   if (!isNaN(num) && num > 0) {
     if (newUnit === 'hectares') {
       const converted = +(num / 2.471).toFixed(2);
       setLandVal(converted);
       setYieldData(prev => ({ ...prev, area_hectares: converted }));
     } else {
       const converted = +(num * 2.471).toFixed(2);
       setLandVal(converted);
       setYieldData(prev => ({ ...prev, area_hectares: +(converted / 2.471).toFixed(2) }));
     }
   }
 };
 async function refresh(){try{let r=await api.get('/api/v1/history');setHistory(r.data)}catch{}}
 useEffect(()=>{api.get('/health').then(()=>setStatus('Connected')).catch(()=>setStatus('Offline')); const token=localStorage.getItem('agri_access_token'); if(!token){setAuthReady(true);return;} api.get('/api/v1/auth/me').then(r=>{setUser(r.data);refresh();}).catch(()=>{localStorage.removeItem('agri_access_token');setUser(null);}).finally(()=>setAuthReady(true));},[]);
 async function submitAuth(e){
   e.preventDefault();
   setAuthBusy(true);
   setAuthError('');
   setAuthSuccess('');
   try{
     if (authMode === 'register') {
       const payload = authForm;
       await api.post('/api/v1/auth/register', payload);
       setAuthMode('login');
       setAuthForm({ full_name: '', email: payload.email, password: '' });
       setAuthSuccess(t('Account created successfully! Please log in with your email and password.'));
     } else {
       const payload = { email: authForm.email, password: authForm.password };
       const r = await api.post('/api/v1/auth/login', payload);
       localStorage.setItem('agri_access_token', r.data.access_token);
       setUser(r.data.user);
       setAuthReady(true);
       refresh();
     }
   }catch(err){
     setAuthError(err.response?.data?.detail || 'Unable to authenticate. Please try again.');
   }finally{
     setAuthBusy(false);
   }
 }
 function logout(){localStorage.removeItem('agri_access_token');setUser(null);setHistory([]);setResult(null);setPage('home');setAuthSuccess('');setAuthError('');}
 async function post(path,data){setBusy(true);setNotice('');setResult(null);try{let r=await api.post(path,data);setResult(r.data);refresh()}catch(e){setNotice(e.response?.data?.detail||'API unavailable. Start FastAPI and retry.')}finally{setBusy(false)}}
 async function disease(file){if(!file)return;let f=new FormData();f.append('file',file);post('/api/v1/predict/disease',f)}
 const Field=({label,value,onChange,type='number'})=><label className="block text-sm font-medium capitalize text-slate-700">{t(label.replaceAll('_',' '))}<input className="mt-1 w-full rounded-lg border border-slate-200 p-3" type={type} min={type==='number'?0:undefined} step={type==='number'?'any':undefined} value={value} onChange={e=>onChange(type==='text'?e.target.value:(e.target.value===''?'':Number(e.target.value)))}/></label>;
 if(!authReady) return <div className="grid min-h-screen place-items-center text-emerald-800">Loading your account…</div>;
 if(!user) return <AuthScreen mode={authMode} setMode={setAuthMode} form={authForm} setForm={setAuthForm} onSubmit={submitAuth} busy={authBusy} error={authError} setAuthError={setAuthError} successMsg={authSuccess} setSuccessMsg={setAuthSuccess} t={t} language={language} setLanguage={setLanguage}/>;
 return <div className="min-h-screen lg:flex">
 <aside className="bg-emerald-950 p-6 text-white lg:min-h-screen lg:w-64"><div className="mb-8 flex items-center gap-3"><Sprout size={30}/><div><b className="text-xl">AgriSmart AI</b><p className="text-xs text-emerald-200">Smart farming assistant</p></div></div><p className="mb-3 text-xs uppercase tracking-widest text-emerald-300">Workspace</p>{nav.map(([id,label])=><button key={id} onClick={()=>{setPage(id);setResult(null);setNotice('')}} className={'mb-1 block w-full rounded-xl px-4 py-3 text-left text-sm '+(page===id?'bg-emerald-700':'text-emerald-100 hover:bg-emerald-900')}>{t(label)}</button>)}<p className="mt-8 rounded-xl border border-emerald-800 p-3 text-xs text-emerald-200">{t('Decision-support only. Verify advice with local agricultural experts.')}</p></aside>
 <main className="min-w-0 flex-1 p-5 md:p-9"><header className="mb-7 flex flex-wrap items-center justify-between gap-3"><div><p className="text-sm text-slate-500">{t('Smart Agriculture Platform')}</p><h1 className="text-2xl font-bold">{t(nav.find(x=>x[0]===page)?.[1])}</h1></div><div className="flex items-center gap-2"><label className="text-sm text-slate-600">{t('Farmer language')}</label><select aria-label="Farmer language" className="rounded-lg border bg-white px-3 py-2 text-sm" value={language} onChange={e=>setLanguage(e.target.value)}>{languages.map(l=><option key={l.code} value={l.code}>{l.label}</option>)}</select><span className="rounded-full border bg-white px-3 py-2 text-xs">{t('API')}: {t(status)}</span><span className="text-sm text-slate-600">{user.full_name}</span><button onClick={logout} className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm">{t('Sign out')}</button></div></header>
 {notice&&<div className="mb-4 flex gap-2 rounded-xl bg-amber-50 p-3 text-sm text-amber-900"><AlertCircle size={18}/>{t(notice)}</div>}
 {result&&<section className={box+' mb-5'}><b className="text-lg">{t(result.recommendations?'Suggested crop options':'Result')}</b><ResultView result={result} language={language} t={t}/></section>}
 {page==='home'&&<><div className="mb-6 rounded-3xl bg-gradient-to-r from-emerald-950 to-green-700 p-8 text-white"><p className="text-emerald-100">{t('Farming decisions supported by data')}</p><h2 className="mt-2 text-3xl font-bold">{t('Grow smarter with agriculture intelligence.')}</h2><p className="mt-3 max-w-2xl text-emerald-100">{t('Start with simple farm details—no soil lab report needed—or use advanced AI tools when detailed data is available.')}</p></div><div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">{[['crop',Sprout,'Crop recommendation','Get broad crop options using location, season and irrigation details.'],['disease',Leaf,'Disease detection','Diagnose diseases in crop leaves, fruits, and vegetables.'],['fert',FlaskConical,'Fertilizer guidance','Review NPK values and safe next steps.'],['yield',TrendingUp,'Yield prediction','Estimate yield using historical data.'],['weather',CloudSun,'Weather insights','View a local forecast.']].map(([id,Icon,title,desc])=><button key={id} onClick={()=>setPage(id)} className={box+' text-left hover:border-emerald-400'}><Icon className="mb-4 text-emerald-700"/><b>{t(title)}</b><p className="mt-2 text-sm text-slate-500">{t(desc)}</p><p className="mt-4 text-sm font-semibold text-emerald-700">{t('Open module →')}</p></button>)}</div></>}
 {page==='crop'&&<section className={box}><h2 className="mb-2 text-xl font-bold">{t('Crop recommendation')}</h2><p className="mb-4 text-sm text-slate-500">{t('Choose the mode that matches the information you have. Soil lab values are not required in Basic Farmer Mode.')}</p><div className="mb-5 flex flex-wrap gap-2"><button onClick={()=>{setCropMode('basic');setResult(null)}} className={'rounded-xl px-4 py-2 text-sm '+(cropMode==='basic'?'bg-emerald-700 text-white':'border')}>{t('Basic Farmer Mode')}</button><button onClick={()=>{setCropMode('advanced');setResult(null)}} className={'rounded-xl px-4 py-2 text-sm '+(cropMode==='advanced'?'bg-emerald-700 text-white':'border')}>{t('Advanced Soil Report Mode')}</button></div>{cropMode==='basic'?<><div className="mb-4 rounded-xl bg-emerald-50 p-3 text-sm text-emerald-900">{t("No NPK or pH values needed. If you do not know your soil type, leave “Don't know”.")}</div><div className="grid gap-4 sm:grid-cols-2"><Field label="Village / Town / District" value={farmer.location} type="text" onChange={v=>setFarmer({...farmer,location:v})}/><Field label="Land size (acres)" value={farmer.land_acres} onChange={v=>setFarmer({...farmer,land_acres:v})}/><label className="block text-sm font-medium text-slate-700">{t('Season')}<select className="mt-1 w-full rounded-lg border border-slate-200 p-3" value={farmer.season} onChange={e=>setFarmer({...farmer,season:e.target.value})}><option>Kharif</option><option>Rabi</option><option>Summer</option></select></label><label className="block text-sm font-medium text-slate-700">{t('Irrigation source')}<select className="mt-1 w-full rounded-lg border border-slate-200 p-3" value={farmer.irrigation} onChange={e=>setFarmer({...farmer,irrigation:e.target.value})}><option>Rain-fed</option><option>Borewell</option><option>Canal</option><option>Other</option></select></label><label className="block text-sm font-medium text-slate-700">{t('Soil type (optional)')}<select className="mt-1 w-full rounded-lg border border-slate-200 p-3" value={farmer.soil_type} onChange={e=>setFarmer({...farmer,soil_type:e.target.value})}><option>Don't know</option><option>Red soil</option><option>Black soil</option><option>Sandy soil</option><option>Loamy soil</option></select></label><Field label="Previous crop (optional)" value={farmer.previous_crop} type="text" onChange={v=>setFarmer({...farmer,previous_crop:v})}/></div><button disabled={busy} onClick={()=>post('/api/v1/recommend/basic',farmer)} className="mt-5 rounded-xl bg-emerald-700 px-5 py-3 text-white">{busy?t('Checking…'):t('Get crop options')}</button><p className="mt-3 text-xs text-amber-700">{t('Basic mode gives broad rule-based options, not a trained ML prediction. Confirm locally before sowing.')}</p></>:<><p className="mb-5 text-sm text-slate-500">Use values from a soil testing report and local weather measurements.</p><div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">{Object.entries(crop).map(([k,v])=><Field key={k} label={k} value={v} onChange={n=>setCrop({...crop,[k]:n})}/>)}</div><button disabled={busy} onClick={()=>post('/api/v1/predict/crop',crop)} className="mt-5 rounded-xl bg-emerald-700 px-5 py-3 text-white">{busy?t('Working…'):t('Run advanced ML model')}</button></>}</section>}
 {page==='disease'&&<section className={box}><h2 className="mb-2 text-xl font-bold">{t('Crop, Fruit & Vegetable Disease Screening')}</h2><p className="mb-5 text-sm text-slate-500">{t('Upload a clear photo of an affected leaf, fruit, or vegetable (JPEG/PNG/WebP, max 8 MB).')}</p><label className="flex cursor-pointer flex-col items-center rounded-2xl border-2 border-dashed border-emerald-200 bg-emerald-50 p-10"><Upload className="mb-3 text-emerald-700"/><b>{t('Select leaf, fruit, or vegetable image')}</b><input className="mt-4" type="file" accept="image/jpeg,image/png,image/webp" onChange={e=>disease(e.target.files?.[0])}/></label><p className="mt-4 text-xs text-amber-700">{t('AI screening is not a confirmed diagnosis.')}</p></section>}
 {page==='fert'&&(
  <section className={box}>
    <h2 className="mb-2 text-xl font-bold">{t('Fertilizer guidance')}</h2>
    <div className="mb-5 rounded-xl bg-emerald-50 p-4 text-xs text-emerald-950 border border-emerald-100 leading-relaxed">
      💡 <b>{t('Fertilizer guidance')}:</b> {t('Fertilizer input guide')}
    </div>
    <div className="grid gap-4 sm:grid-cols-2">
      <label className="block text-sm font-medium capitalize text-slate-700">
        {t('Crop Name')}
        <input list="crop-suggestions" className="mt-1 w-full rounded-lg border border-slate-200 p-3" value={fert.crop} onChange={e=>setFert({...fert,crop:e.target.value})}/>
        <datalist id="crop-suggestions">
          <option value="Rice"/>
          <option value="Wheat"/>
          <option value="Maize"/>
          <option value="Cotton"/>
          <option value="Sugarcane"/>
          <option value="Groundnut"/>
          <option value="Tomato"/>
          <option value="Potato"/>
          <option value="Chickpea"/>
          <option value="Millets"/>
          <option value="Vegetables"/>
        </datalist>
      </label>
      <label className="block text-sm font-medium capitalize text-slate-700">
        {t('Nitrogen (N) kg/ha')}
        <input className="mt-1 w-full rounded-lg border border-slate-200 p-3" type="number" min={0} step="any" value={fert.nitrogen} onChange={e=>setFert({...fert,nitrogen:e.target.value===''?'':Number(e.target.value)})}/>
      </label>
      <label className="block text-sm font-medium capitalize text-slate-700">
        {t('Phosphorus (P) kg/ha')}
        <input className="mt-1 w-full rounded-lg border border-slate-200 p-3" type="number" min={0} step="any" value={fert.phosphorus} onChange={e=>setFert({...fert,phosphorus:e.target.value===''?'':Number(e.target.value)})}/>
      </label>
      <label className="block text-sm font-medium capitalize text-slate-700">
        {t('Potassium (K) kg/ha')}
        <input className="mt-1 w-full rounded-lg border border-slate-200 p-3" type="number" min={0} step="any" value={fert.potassium} onChange={e=>setFert({...fert,potassium:e.target.value===''?'':Number(e.target.value)})}/>
      </label>
    </div>
    <div className="mt-4 flex flex-wrap items-center gap-3">
      <button disabled={busy} onClick={()=>post('/api/v1/predict/fertilizer',fert)} className="rounded-xl bg-emerald-700 px-6 py-3 font-semibold text-white hover:bg-emerald-800 disabled:opacity-50">
        {busy ? t('Checking…') : t('Get guidance')}
      </button>
      <span className="text-xs text-slate-500">
        Sample: 
        <button type="button" onClick={()=>setFert({crop:'Rice',nitrogen:35,phosphorus:25,potassium:30})} className="ml-1 text-emerald-700 underline font-medium">Rice</button> · 
        <button type="button" onClick={()=>setFert({crop:'Wheat',nitrogen:50,phosphorus:20,potassium:25})} className="ml-1 text-emerald-700 underline font-medium">Wheat</button> · 
        <button type="button" onClick={()=>setFert({crop:'Tomato',nitrogen:40,phosphorus:30,potassium:35})} className="ml-1 text-emerald-700 underline font-medium">Tomato</button>
      </span>
    </div>
  </section>
)}
 {page==='yield'&&(
   <section className={box}>
     <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
       <h2 className="text-xl font-bold">{t('Yield Prediction & Harvest Forecast')}</h2>
       <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-800">
         🌾 {t('Current Crop Year')}: 2026
       </span>
     </div>
     <p className="mb-4 text-xs text-slate-500">
       {t('Estimate crop harvest production in bags and quintals based on weather and field inputs.')}
     </p>

     {/* Units Quick Guide Banner */}
     <div className="mb-5 rounded-2xl border border-emerald-200 bg-emerald-50/70 p-4 text-emerald-950">
       <div className="flex items-start gap-2">
         <span className="text-lg">💡</span>
         <div className="text-xs leading-relaxed">
           <b>{t('Yield guide banner')}</b>
           <div className="mt-2.5 flex flex-wrap gap-2 text-2xs font-medium">
             <span className="rounded-md bg-white px-2.5 py-1 border border-emerald-200 text-emerald-900 shadow-2xs">
               📏 1 {t('Acres')} ≈ 0.40 {t('Hectares')} (1 Ha = 2.47 Acres)
             </span>
             <span className="rounded-md bg-white px-2.5 py-1 border border-emerald-200 text-emerald-900 shadow-2xs">
               ⚖️ 1 Quintal = 100 kg (2 standard bags)
             </span>
             <span className="rounded-md bg-white px-2.5 py-1 border border-emerald-200 text-emerald-900 shadow-2xs">
               🚛 1 Tonne = 10 Quintals = 1,000 kg (20 bags)
             </span>
           </div>
         </div>
       </div>
     </div>

     {/* Quick Crop Presets Bar */}
     <div className="mb-5">
       <p className="mb-1.5 text-xs font-semibold uppercase tracking-wider text-slate-600">
         ⚡ {t('Quick Crop Presets')}:
       </p>
       <div className="flex flex-wrap gap-1.5">
         {CROP_PRESETS.map(p => (
           <button
             key={p.crop}
             type="button"
             onClick={() => setYieldData(prev => ({
               ...prev,
               crop: p.crop,
               rainfall_mm: p.rain,
               average_temperature_c: p.temp,
               fertilizer_kg_per_hectare: p.fert
             }))}
             className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
               yieldData.crop.toLowerCase() === p.crop.toLowerCase()
                 ? 'bg-emerald-700 text-white shadow-2xs'
                 : 'border border-slate-200 bg-slate-50 text-slate-700 hover:bg-emerald-50 hover:text-emerald-800'
             }`}
           >
             {t(p.name)}
           </button>
         ))}
       </div>
     </div>

     {/* Form Fields */}
     <div className="grid gap-5 sm:grid-cols-2">
       {/* Crop Name */}
       <div>
         <label className="block text-sm font-medium text-slate-700">
           {t('Crop Name')}
           <input
             list="yield-crop-suggestions"
             className="mt-1 w-full rounded-lg border border-slate-200 p-3 font-medium text-slate-800"
             value={yieldData.crop}
             onChange={e => setYieldData({ ...yieldData, crop: e.target.value })}
             placeholder="e.g. Rice, Wheat, Cotton..."
           />
           <datalist id="yield-crop-suggestions">
             <option value="Rice" />
             <option value="Wheat" />
             <option value="Maize" />
             <option value="Cotton" />
             <option value="Sugarcane" />
             <option value="Groundnut" />
             <option value="Tomato" />
             <option value="Potato" />
             <option value="Chickpea" />
           </datalist>
         </label>
       </div>

       {/* Land Area with Unit Toggle */}
       <div>
         <div className="flex items-center justify-between">
           <label className="text-sm font-medium text-slate-700">
             {t('Land Area')}
           </label>
           <div className="flex rounded-lg border border-slate-200 bg-slate-100 p-0.5 text-xs font-medium">
             <button
               type="button"
               onClick={() => handleUnitSwitch('acres')}
               className={`rounded-md px-2.5 py-1 ${landUnit === 'acres' ? 'bg-white text-emerald-800 shadow-2xs font-bold' : 'text-slate-600 hover:text-slate-900'}`}
             >
               {t('Acres')}
             </button>
             <button
               type="button"
               onClick={() => handleUnitSwitch('hectares')}
               className={`rounded-md px-2.5 py-1 ${landUnit === 'hectares' ? 'bg-white text-emerald-800 shadow-2xs font-bold' : 'text-slate-600 hover:text-slate-900'}`}
             >
               {t('Hectares')}
             </button>
           </div>
         </div>
         <div className="relative mt-1">
           <input
             className="w-full rounded-lg border border-slate-200 p-3 pr-20 font-medium"
             type="number"
             min={0.1}
             step="any"
             value={landVal}
             onChange={e => handleLandChange(e.target.value)}
           />
           <span className="pointer-events-none absolute right-3 top-3.5 text-xs font-semibold text-slate-400">
             {landUnit === 'acres' ? t('Acres') : t('Hectares')}
           </span>
         </div>
         <p className="mt-1 text-2xs text-slate-500">
           {landUnit === 'acres'
             ? `≈ ${yieldData.area_hectares || (landVal / 2.471).toFixed(2)} ${t('Hectares')} (1 Ha = 2.47 Acres)`
             : `≈ ${(landVal * 2.471).toFixed(2)} ${t('Acres')}`}
         </p>
       </div>

       {/* Seasonal Rainfall */}
       <div>
         <label className="block text-sm font-medium text-slate-700">
           {t('Rainfall (mm)')}
           <input
             className="mt-1 w-full rounded-lg border border-slate-200 p-3 font-medium"
             type="number"
             min={0}
             step="any"
             value={yieldData.rainfall_mm}
             onChange={e => setYieldData({ ...yieldData, rainfall_mm: e.target.value === '' ? '' : Number(e.target.value) })}
           />
         </label>
         <div className="mt-1.5 flex flex-wrap gap-1">
           <button
             type="button"
             onClick={() => setYieldData(prev => ({ ...prev, rainfall_mm: 350 }))}
             className="rounded border border-slate-200 bg-slate-50 px-2 py-0.5 text-2xs text-slate-600 hover:border-emerald-300 hover:bg-emerald-50"
           >
             ☀️ 350 mm ({t('Winter / Rabi (Cool)')})
           </button>
           <button
             type="button"
             onClick={() => setYieldData(prev => ({ ...prev, rainfall_mm: 850 }))}
             className="rounded border border-slate-200 bg-slate-50 px-2 py-0.5 text-2xs text-slate-600 hover:border-emerald-300 hover:bg-emerald-50"
           >
             🌧️ 850 mm ({t('Monsoon / Kharif (Normal)')})
           </button>
           <button
             type="button"
             onClick={() => setYieldData(prev => ({ ...prev, rainfall_mm: 1200 }))}
             className="rounded border border-slate-200 bg-slate-50 px-2 py-0.5 text-2xs text-slate-600 hover:border-emerald-300 hover:bg-emerald-50"
           >
             🌊 1200 mm ({t('High Rainfall / Coastal')})
           </button>
         </div>
       </div>

       {/* Average Temperature */}
       <div>
         <div className="flex items-center justify-between">
           <label className="text-sm font-medium text-slate-700">
             {t('Average Temperature (°C)')}
           </label>
           {weather?.current && (
             <button
               type="button"
               onClick={() => setYieldData(prev => ({ ...prev, average_temperature_c: weather.current.temperature_2m }))}
               className="text-2xs font-semibold text-emerald-700 underline"
             >
               🌤️ {weather.current.temperature_2m}°C ({weatherLocation.split(',')[0]})
             </button>
           )}
         </div>
         <input
           className="mt-1 w-full rounded-lg border border-slate-200 p-3 font-medium"
           type="number"
           step="any"
           value={yieldData.average_temperature_c}
           onChange={e => setYieldData({ ...yieldData, average_temperature_c: e.target.value === '' ? '' : Number(e.target.value) })}
         />
         <div className="mt-1.5 flex flex-wrap gap-1">
           <button
             type="button"
             onClick={() => setYieldData(prev => ({ ...prev, average_temperature_c: 18 }))}
             className="rounded border border-slate-200 bg-slate-50 px-2 py-0.5 text-2xs text-slate-600 hover:border-emerald-300 hover:bg-emerald-50"
           >
             ❄️ 18°C ({t('Winter / Rabi (Cool)')})
           </button>
           <button
             type="button"
             onClick={() => setYieldData(prev => ({ ...prev, average_temperature_c: 26 }))}
             className="rounded border border-slate-200 bg-slate-50 px-2 py-0.5 text-2xs text-slate-600 hover:border-emerald-300 hover:bg-emerald-50"
           >
             ⛅ 26°C ({t('Monsoon / Kharif (Normal)')})
           </button>
           <button
             type="button"
             onClick={() => setYieldData(prev => ({ ...prev, average_temperature_c: 32 }))}
             className="rounded border border-slate-200 bg-slate-50 px-2 py-0.5 text-2xs text-slate-600 hover:border-emerald-300 hover:bg-emerald-50"
           >
             🔥 32°C ({t('Summer / Dry (Warm)')})
           </button>
         </div>
       </div>

       {/* Fertilizer Usage */}
       <div>
         <label className="block text-sm font-medium text-slate-700">
           {t('Fertilizer (kg/ha)')}
           <input
             className="mt-1 w-full rounded-lg border border-slate-200 p-3 font-medium"
             type="number"
             min={0}
             step="any"
             value={yieldData.fertilizer_kg_per_hectare}
             onChange={e => setYieldData({ ...yieldData, fertilizer_kg_per_hectare: e.target.value === '' ? '' : Number(e.target.value) })}
           />
         </label>
         <div className="mt-1 flex items-center justify-between text-2xs text-slate-500">
           <span>
             ≈ {((yieldData.fertilizer_kg_per_hectare || 0) / 2.471).toFixed(0)} kg/acre (~{(((yieldData.fertilizer_kg_per_hectare || 0) / 2.471) / 50).toFixed(1)} bags/acre)
           </span>
           <div className="flex gap-1">
             <button
               type="button"
               onClick={() => setYieldData(prev => ({ ...prev, fertilizer_kg_per_hectare: 60 }))}
               className="rounded border border-slate-200 px-1.5 py-0.5 hover:bg-emerald-50"
             >
               {t('Low / Organic')} (60)
             </button>
             <button
               type="button"
               onClick={() => setYieldData(prev => ({ ...prev, fertilizer_kg_per_hectare: 100 }))}
               className="rounded border border-slate-200 px-1.5 py-0.5 hover:bg-emerald-50"
             >
               {t('Standard NPK')} (100)
             </button>
             <button
               type="button"
               onClick={() => setYieldData(prev => ({ ...prev, fertilizer_kg_per_hectare: 160 }))}
               className="rounded border border-slate-200 px-1.5 py-0.5 hover:bg-emerald-50"
             >
               {t('High Yield')} (160)
             </button>
           </div>
         </div>
       </div>

       {/* Harvest Year */}
       <div>
         <label className="block text-sm font-medium text-slate-700">
           {t('Harvest Year')}
           <select
             className="mt-1 w-full rounded-lg border border-slate-200 p-3 font-medium text-slate-800"
             value={yieldData.year}
             onChange={e => setYieldData({ ...yieldData, year: Number(e.target.value) })}
           >
             <option value={2026}>2026 ({t('Current Crop Year')})</option>
             <option value={2027}>2027</option>
             <option value={2025}>2025</option>
             <option value={2024}>2024</option>
           </select>
         </label>
       </div>
     </div>

     {/* Action Bar */}
     <div className="mt-6 flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 pt-4">
       <button
         disabled={busy}
         onClick={() => post('/api/v1/predict/yield', yieldData)}
         className="inline-flex items-center gap-2 rounded-xl bg-emerald-700 px-8 py-3.5 font-bold text-white shadow-sm hover:bg-emerald-800 disabled:opacity-50"
       >
         <span>🚜</span>
         {busy ? t('Checking…') : t('Estimate yield')}
       </button>

       <span className="text-xs text-slate-500">
         Sample: 
         <button type="button" onClick={() => setYieldData({ crop: 'Rice', area_hectares: 1.01, rainfall_mm: 900, average_temperature_c: 26, fertilizer_kg_per_hectare: 100, year: 2026 })} className="ml-1 text-emerald-700 underline font-medium">{t('Paddy (Rice)')}</button> · 
         <button type="button" onClick={() => setYieldData({ crop: 'Wheat', area_hectares: 1.01, rainfall_mm: 450, average_temperature_c: 18, fertilizer_kg_per_hectare: 120, year: 2026 })} className="ml-1 text-emerald-700 underline font-medium">{t('Wheat')}</button> · 
         <button type="button" onClick={() => setYieldData({ crop: 'Cotton', area_hectares: 1.01, rainfall_mm: 700, average_temperature_c: 27, fertilizer_kg_per_hectare: 100, year: 2026 })} className="ml-1 text-emerald-700 underline font-medium">{t('Cotton')}</button>
       </span>
     </div>
   </section>
 )}
 {page==='weather'&&<section className={box}><h2 className="mb-2 text-xl font-bold">{t('Weather insights')}</h2><p className="mb-4 text-sm text-slate-500">{t('Enter a village, town or district. We will look up its coordinates automatically.')}</p><Field label="Your location" value={weatherLocation} type="text" onChange={setWeatherLocation}/><button disabled={busy} onClick={async()=>{setBusy(true);setNotice('');try{const found=await api.get('/api/v1/location/lookup',{params:{name:weatherLocation}});const place=found.data.results?.[0];if(!place)throw new Error('Location not found. Try a nearby town or district.');const r=await api.get('/api/v1/weather',{params:{latitude:place.latitude,longitude:place.longitude}});setWeather(r.data);setResult(null);}catch(e){setNotice(e.response?.data?.detail||e.message||'Weather request failed')}finally{setBusy(false)}}} className="mt-5 rounded-xl bg-emerald-700 px-5 py-3 text-white">{busy?t('Finding weather…'):t('Get local forecast')}</button>{weather?.current&&<><div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">{[['Temperature',weather.current.temperature_2m+'°C'],['Humidity',weather.current.relative_humidity_2m+'%'],['Precipitation',weather.current.precipitation+' mm'],['Wind speed',weather.current.wind_speed_10m+' km/h']].map(([a,b])=><div className={box} key={a}><p className="text-sm text-slate-500">{t(a)}</p><b className="text-2xl">{b}</b></div>)}</div><WeatherAdvice weather={weather} language={language}/></>}</section>}
 {page==='history'&&<section className={box}><div className="mb-4 flex justify-between"><h2 className="text-xl font-bold">{t('Prediction history')}</h2><button onClick={refresh} className="rounded-lg border px-3 py-2 text-sm">{t('Refresh')}</button></div>{history.length===0?<p className="text-sm text-slate-500">{t('No predictions saved yet.')}</p>:<div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead><tr className="border-b"><th className="p-2">{t('Module')}</th><th className="p-2">{t('Result')}</th><th className="p-2">{t('Date')}</th></tr></thead><tbody>{history.map(r=><tr className="border-b" key={r.id}><td className="p-2">{t(r.module)}</td><td className="max-w-xs truncate p-2">{JSON.stringify(r.result)}</td><td className="p-2">{r.created_at?new Date(r.created_at).toLocaleString():'—'}</td></tr>)}</tbody></table></div>}</section>}
 <footer className="mt-8 text-xs text-slate-400">AgriSmart AI · Educational decision support</footer></main></div>
}

function ResultView({ result, language, t }) {
  const tr = translateCropResult(result, language);
  if (Array.isArray(result.recommendations)) {
    return (
      <>
        <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {tr.recommendations.map((item, i) => (
            <div key={item.crop} className="rounded-xl border border-emerald-100 bg-emerald-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-emerald-700">{t('Option')} {i + 1}</p>
              <h3 className="mt-1 text-lg font-bold text-emerald-950">{item.crop}</h3>
              <p className="mt-2 text-sm text-slate-700">{t('Water need')}: {item.water}</p>
              <p className="mt-2 text-sm text-slate-600">{item.note}</p>
            </div>
          ))}
        </div>
        <p className="mt-4 text-sm text-slate-700">{tr.soil_note}</p>
        <p className="mt-2 rounded-xl bg-amber-50 p-3 text-sm text-amber-900">{tr.next_step}</p>
        <p className="mt-2 text-xs text-slate-500">{tr.limitations}</p>
      </>
    );
  }
  if (result.mode === 'setup_required') {
    return (
      <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 p-4 text-amber-900">
        <b className="text-base">{t('setup_required')}</b>
        <p className="mt-1 text-sm">{t(result.message)}</p>
      </div>
    );
  }
  if (result.lowest_reported_nutrient || result.advisory) {
    const adv = result.advisory?.[language] || result.advisory?.en;
    const nutrients = [
      { key: 'N', name: t('Nitrogen (N)'), cur: result.entered_npk?.N, tar: result.target_npk?.N, def: result.deficits?.N },
      { key: 'P', name: t('Phosphorus (P)'), cur: result.entered_npk?.P, tar: result.target_npk?.P, def: result.deficits?.P },
      { key: 'K', name: t('Potassium (K)'), cur: result.entered_npk?.K, tar: result.target_npk?.K, def: result.deficits?.K },
    ];

    return (
      <div className="mt-4 space-y-5">
        <div className="rounded-2xl border border-emerald-200 bg-emerald-50/80 p-5 text-emerald-950">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-emerald-700">{t('Fertilizer guidance')}</p>
              <h3 className="mt-1 text-2xl font-bold">{adv?.title || `${t('crop')}: ${result.crop}`}</h3>
            </div>
            {result.lowest_reported_nutrient && (
              <div className="rounded-full bg-emerald-700 px-4 py-1.5 text-xs font-bold text-white shadow-xs">
                {t('Most Deficient Nutrient')}: {t(result.lowest_reported_nutrient)}
              </div>
            )}
          </div>
          {adv?.status_summary && (
            <p className="mt-3 text-sm text-slate-700 leading-relaxed">{adv.status_summary}</p>
          )}
          {!adv && result.observation && (
            <p className="mt-3 text-sm text-slate-700 leading-relaxed">{result.observation}</p>
          )}
        </div>

        {result.entered_npk && (
          <div>
            <h4 className="text-sm font-bold uppercase tracking-wider text-slate-700">{t('Soil Nutrient Deficit Analysis')}</h4>
            <div className="mt-2 grid gap-3 sm:grid-cols-3">
              {nutrients.map(n => (
                <div key={n.key} className="rounded-xl border border-slate-200 bg-white p-4 shadow-2xs">
                  <div className="flex items-center justify-between">
                    <b className="text-base text-slate-800">{n.name}</b>
                    <span className={'rounded-md px-2 py-0.5 text-xs font-bold ' + (n.def > 0 ? 'bg-rose-100 text-rose-700' : 'bg-emerald-100 text-emerald-700')}>
                      {n.def > 0 ? `-${n.def} kg/ha` : t('Optimal / Sufficient')}
                    </span>
                  </div>
                  <div className="mt-3 space-y-1.5 text-xs text-slate-600">
                    <div className="flex justify-between">
                      <span>{t('Current Soil')}:</span>
                      <span className="font-semibold text-slate-800">{n.cur} kg/ha</span>
                    </div>
                    <div className="flex justify-between">
                      <span>{t('Target Benchmark')}:</span>
                      <span className="font-semibold text-slate-800">{n.tar} kg/ha</span>
                    </div>
                    <div className="flex justify-between pt-1 border-t border-slate-100 font-bold">
                      <span className={n.def > 0 ? 'text-rose-600' : 'text-emerald-600'}>{t('Deficit')}:</span>
                      <span className={n.def > 0 ? 'text-rose-600' : 'text-emerald-600'}>{n.def} kg/ha</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {adv?.fertilizers_needed && (
          <div>
            <h4 className="text-sm font-bold uppercase tracking-wider text-slate-700">{t('Commercial Fertilizers Required')}</h4>
            <div className="mt-2 grid gap-3 sm:grid-cols-3">
              {adv.fertilizers_needed.map((f, i) => (
                <div key={i} className="rounded-xl border border-emerald-100 bg-gradient-to-br from-white to-emerald-50/50 p-4 shadow-2xs">
                  <p className="text-xs font-bold text-emerald-800 uppercase tracking-wide">{f.name}</p>
                  <p className="mt-2 text-base font-extrabold text-emerald-950">{f.amount}</p>
                  <p className="mt-2 text-xs text-slate-600 leading-snug">{f.note}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {adv?.application_schedule && (
          <div>
            <h4 className="text-sm font-bold uppercase tracking-wider text-slate-700">{t('Split Application Schedule')}</h4>
            <div className="mt-2 space-y-2">
              {adv.application_schedule.map((s, i) => (
                <div key={i} className="flex gap-3 rounded-xl border border-slate-200 bg-white p-3.5 shadow-2xs">
                  <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-emerald-700 text-xs font-bold text-white">
                    {i + 1}
                  </div>
                  <div>
                    <b className="text-sm text-slate-900">{s.stage}</b>
                    <p className="mt-1 text-xs text-slate-700 leading-relaxed">{s.action}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {adv?.organic_and_micronutrient_tips && (
          <div className="rounded-xl border border-amber-200 bg-amber-50/60 p-4">
            <p className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-amber-900">
              <span>🌾</span> {t('Organic & Micronutrient Tips')}
            </p>
            <p className="mt-1.5 text-xs text-amber-950 leading-relaxed">{adv.organic_and_micronutrient_tips}</p>
          </div>
        )}

        <p className="rounded-xl border border-slate-200 bg-slate-50 p-3 text-xs text-slate-600">
          {adv?.safety_disclaimer || t(result.guidance)}
        </p>
      </div>
    );
  }
  if (result.predicted_class) {
    const adv = result.treatment?.[language] || result.treatment?.en;
    const isHealthy = result.predicted_class.toLowerCase().includes('healthy');
    const organIcon = result.organ_type === 'Fruit' ? '🍎' : result.organ_type === 'Vegetable' ? '🥔' : '🌿';
    return (
      <div className="mt-4 space-y-4">
        <div className={'rounded-2xl border p-5 ' + (isHealthy ? 'border-emerald-200 bg-emerald-50 text-emerald-950' : 'border-rose-200 bg-rose-50/70 text-slate-900')}>
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">{t('Crop, Fruit & Vegetable Disease Screening')}</p>
                {result.organ_type && (
                  <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-bold text-slate-700 border border-slate-200">
                    {organIcon} {t(result.organ_type)}
                  </span>
                )}
                {result.crop && (
                  <span className="rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-bold text-emerald-800 border border-emerald-200">
                    {t(result.crop)}
                  </span>
                )}
              </div>
              <h3 className="mt-1 text-2xl font-bold">{adv?.disease_name || t(result.predicted_class)}</h3>
            </div>
            <div className="flex items-center gap-2">
              <span className={'rounded-full px-3 py-1 text-xs font-bold ' + (isHealthy ? 'bg-emerald-200 text-emerald-800' : 'bg-rose-200 text-rose-800')}>
                {adv?.severity ? `${t('Severity')}: ${adv.severity}` : t('predicted_class')}
              </span>
              <span className="rounded-full bg-white px-3 py-1 text-xs font-semibold text-slate-700 shadow-xs">
                {t('Confidence')}: {result.confidence_percent}%
              </span>
            </div>
          </div>
        </div>

        {adv && (
          <div className="space-y-3">
            <h4 className="text-base font-bold text-slate-900">{t('Treatment & Cure Recommendations')}</h4>
            <div className="grid gap-3 md:grid-cols-2">
              <div className="rounded-xl border border-rose-100 bg-white p-4 shadow-2xs">
                <p className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-rose-700">
                  <span>🧪</span> {t('Chemical Pesticide / Fungicide')}
                </p>
                <p className="mt-2 text-sm text-slate-800">{adv.chemical_control}</p>
              </div>

              <div className="rounded-xl border border-emerald-100 bg-white p-4 shadow-2xs">
                <p className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-emerald-700">
                  <span>🌿</span> {t('Organic & Biological Remedy')}
                </p>
                <p className="mt-2 text-sm text-slate-800">{adv.organic_control}</p>
              </div>

              <div className="rounded-xl border border-amber-100 bg-white p-4 shadow-2xs">
                <p className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-amber-700">
                  <span>🌱</span> {t('Fertilizer & Nutrient Guidance')}
                </p>
                <p className="mt-2 text-sm text-slate-800">{adv.fertilizer_management}</p>
              </div>

              <div className="rounded-xl border border-sky-100 bg-white p-4 shadow-2xs">
                <p className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-sky-700">
                  <span>💧</span> {t('How to Apply & Spray Instructions')}
                </p>
                <p className="mt-2 text-sm text-slate-800">{adv.application_instructions}</p>
              </div>
            </div>

            {adv.preventive_measures && (
              <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                <p className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-700">
                  <span>🛡️</span> {t('Preventive Measures')}
                </p>
                <p className="mt-2 text-sm text-slate-700">{adv.preventive_measures}</p>
              </div>
            )}
          </div>
        )}

        {result.disclaimer && (
          <p className="rounded-xl bg-amber-50 p-3 text-xs text-amber-900 border border-amber-200">
            {t(result.disclaimer)}
          </p>
        )}
      </div>
    );
  }
  if (result.estimated_yield_tonnes_per_hectare !== undefined) {
    const adv = result.advisory?.[language] || result.advisory?.en;
    const yHa = result.estimated_yield_tonnes_per_hectare;
    const yTot = result.estimated_total_tonnes;
    const qHa = result.quintals_per_hectare || (yHa * 10).toFixed(1);
    const qAcre = result.quintals_per_acre || ((yHa * 10) / 2.471).toFixed(1);
    const qTot = result.total_quintals || (yTot * 10).toFixed(1);
    const bags = result.total_bags_50kg || Math.round((yTot * 1000) / 50);
    const areaHa = result.area_hectares || 1;
    const areaAcres = result.area_acres || (areaHa * 2.471).toFixed(1);

    return (
      <div className="mt-4 space-y-5">
        {/* Header Summary Card */}
        <div className="rounded-2xl border border-emerald-200 bg-gradient-to-br from-emerald-50 to-green-50 p-5 text-emerald-950">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-emerald-700">{t('Yield Prediction & Harvest Forecast')}</p>
              <h3 className="mt-1 text-2xl font-black">{t(result.crop) || result.crop} — {yHa} t/ha</h3>
              <p className="mt-1 text-xs text-slate-600">
                ≈ <span className="font-bold text-emerald-900">{qAcre} quintals / acre</span> ({qHa} quintals / hectare)
              </p>
            </div>
            {adv?.performance_rating && (
              <div className="rounded-full bg-emerald-700 px-4 py-1.5 text-xs font-bold text-white shadow-xs">
                {adv.performance_rating}
              </div>
            )}
          </div>
          {adv?.summary && (
            <p className="mt-3 text-sm text-slate-700 leading-relaxed border-t border-emerald-200/60 pt-3">{adv.summary}</p>
          )}
        </div>

        {/* Harvest Production Grid */}
        <div>
          <h4 className="text-sm font-bold uppercase tracking-wider text-slate-700">{t('Total Harvest Production')}</h4>
          <div className="mt-2 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {/* Standard 50 kg Bags - Primary Metric */}
            <div className="rounded-xl border-2 border-emerald-400 bg-emerald-50/70 p-4 shadow-2xs">
              <p className="text-xs font-bold uppercase tracking-wider text-emerald-800">🛍️ {t('Standard 50 kg Bags')}</p>
              <p className="mt-1 text-3xl font-black text-emerald-950">~{bags} <span className="text-sm font-normal text-slate-600">bags</span></p>
              <p className="text-xs text-emerald-700 mt-1 font-medium">50 kg standard market bag</p>
            </div>
            {/* Total Quintals */}
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-2xs">
              <p className="text-xs font-medium text-slate-500">{t('Total Production in Quintals')}</p>
              <p className="mt-1 text-2xl font-black text-emerald-950">{qTot} <span className="text-sm font-normal text-slate-600">quintals</span></p>
              <p className="text-xs text-slate-500 mt-1">1 quintal = 100 kg</p>
            </div>
            {/* Total Production (Tonnes) */}
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-2xs">
              <p className="text-xs font-medium text-slate-500">{t('Total Production (Tonnes)')}</p>
              <p className="mt-1 text-2xl font-black text-emerald-950">{yTot} <span className="text-sm font-normal text-slate-600">tonnes</span></p>
              <p className="text-xs text-slate-500 mt-1">1 tonne = 10 quintals</p>
            </div>
            {/* Farm Area */}
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-2xs">
              <p className="text-xs font-medium text-slate-500">{t('Land Area')}</p>
              <p className="mt-1 text-2xl font-bold text-slate-800">{areaAcres} <span className="text-sm font-normal text-slate-600">acres</span></p>
              <p className="text-xs text-slate-500 mt-1">({areaHa} ha)</p>
            </div>
          </div>
        </div>

        {/* Key Production Factors */}
        {adv?.production_factors && (
          <div>
            <h4 className="text-sm font-bold uppercase tracking-wider text-slate-700">{t('Key Production Factors')}</h4>
            <div className="mt-2 grid gap-3 sm:grid-cols-3">
              {adv.production_factors.map((factor, i) => (
                <div key={i} className="rounded-xl border border-emerald-100 bg-gradient-to-br from-white to-emerald-50/50 p-4 shadow-2xs">
                  <p className="text-xs text-slate-700 leading-relaxed">{factor}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Post-Harvest & Market Advisory */}
        {adv?.harvest_advice && (
          <div className="rounded-xl border border-amber-200 bg-amber-50/60 p-4">
            <p className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-amber-900">
              <span>🌾</span> {t('Post-Harvest & Market Advice')}
            </p>
            <p className="mt-1.5 text-xs text-amber-950 leading-relaxed">{adv.harvest_advice}</p>
          </div>
        )}

        {/* Farmer Units Guide Note */}
        <p className="rounded-xl border border-slate-200 bg-slate-50 p-3 text-xs text-slate-600">
          💡 <b>{t('Farmer Guide')}:</b> {t('Farmer Guide text')}
        </p>
      </div>
    );
  }
  if (result.prediction) {
    return (
      <div className="mt-4 rounded-xl border border-emerald-100 bg-emerald-50 p-4">
        <p className="text-xs uppercase text-emerald-700">{t('Crop recommendation')}</p>
        <h3 className="text-2xl font-bold text-emerald-950">{t(result.prediction)}</h3>
        {result.confidence_percent && <p className="mt-1 text-sm text-slate-600">{t('confidence_percent')}: {result.confidence_percent}%</p>}
      </div>
    );
  }
  return <pre className="mt-3 overflow-auto whitespace-pre-wrap text-sm">{JSON.stringify(tr, null, 2)}</pre>;
}

function AuthScreen({mode, setMode, form, setForm, onSubmit, busy, error, setAuthError, successMsg, setSuccessMsg, t, language, setLanguage}) {
 const register = mode === 'register';
 const input = 'mt-1 w-full rounded-xl border border-slate-200 p-3 outline-none focus:border-emerald-600 font-medium text-slate-800 transition-colors';

 const switchMode = (newMode) => {
   setMode(newMode);
   if (setAuthError) setAuthError('');
   if (setSuccessMsg) setSuccessMsg('');
 };

 return (
   <main className="grid min-h-screen place-items-center bg-emerald-50/70 p-4">
     <section className="w-full max-w-md rounded-3xl border border-emerald-100 bg-white p-7 shadow-xl">
       {/* Brand header with language switcher */}
       <div className="mb-6 flex items-center justify-between">
         <div className="flex items-center gap-3 text-emerald-800">
           <Sprout size={34}/>
           <div>
             <h1 className="text-2xl font-black tracking-tight">AgriSmart AI</h1>
             <p className="text-xs text-slate-500 font-medium">{t('Smart farming assistant')}</p>
           </div>
         </div>
         <select
           aria-label={t('Farmer language')}
           className="rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-medium text-slate-700 shadow-2xs"
           value={language}
           onChange={e => setLanguage(e.target.value)}
         >
           {languages.map(l => (
             <option key={l.code} value={l.code}>{l.label}</option>
           ))}
         </select>
       </div>

       {/* Mode Navigation Tabs */}
       <div className="mb-6 grid grid-cols-2 gap-1 rounded-2xl bg-slate-100 p-1">
         <button
           type="button"
           onClick={() => switchMode('login')}
           className={`rounded-xl py-2.5 text-sm font-bold transition-all ${
             !register
               ? 'bg-white text-emerald-800 shadow-sm'
               : 'text-slate-600 hover:text-slate-900'
           }`}
         >
           🔑 {t('Log in')}
         </button>
         <button
           type="button"
           onClick={() => switchMode('register')}
           className={`rounded-xl py-2.5 text-sm font-bold transition-all ${
             register
               ? 'bg-white text-emerald-800 shadow-sm'
               : 'text-slate-600 hover:text-slate-900'
           }`}
         >
           ✨ {t('Create account')}
         </button>
       </div>

       {/* Form Header */}
       <h2 className="text-xl font-bold text-slate-900">{t(register ? 'Create farmer account' : 'Welcome back')}</h2>
       <p className="mt-1 text-xs text-slate-500">
         {t(register ? 'Register to save and view your own farming predictions.' : 'Log in to access your farming dashboard and saved history.')}
       </p>

       {/* Success Alert Banner */}
       {successMsg && (
         <div className="mt-4 rounded-xl border border-emerald-200 bg-emerald-50 p-3.5 text-xs font-semibold text-emerald-900 flex items-start gap-2 shadow-2xs">
           <span className="text-sm">✅</span>
           <span className="leading-relaxed">{successMsg}</span>
         </div>
       )}

       {/* Error Alert Banner */}
       {error && (
         <div role="alert" className="mt-4 rounded-xl border border-rose-200 bg-rose-50 p-3.5 text-xs font-semibold text-rose-700 flex items-start gap-2 shadow-2xs">
           <span className="text-sm">⚠️</span>
           <span className="leading-relaxed">{error}</span>
         </div>
       )}

       {/* Input Form */}
       <form onSubmit={onSubmit} className="mt-5 space-y-4">
         {register && (
           <label className="block text-sm font-medium text-slate-700">
             {t('Full name')}
             <input
               required
               minLength={2}
               maxLength={120}
               autoComplete="name"
               placeholder="e.g. Surendra"
               className={input}
               value={form.full_name}
               onChange={e => setForm({ ...form, full_name: e.target.value })}
             />
           </label>
         )}

         <label className="block text-sm font-medium text-slate-700">
           {t('Email address')}
           <input
             required
             type="email"
             autoComplete="email"
             placeholder="name@example.com"
             className={input}
             value={form.email}
             onChange={e => setForm({ ...form, email: e.target.value })}
           />
         </label>

         <label className="block text-sm font-medium text-slate-700">
           {t('Password')}
           <input
             required
             minLength={register ? 8 : 1}
             maxLength={128}
             type="password"
             autoComplete={register ? 'new-password' : 'current-password'}
             placeholder="••••••••"
             className={input}
             value={form.password}
             onChange={e => setForm({ ...form, password: e.target.value })}
           />
           {register && (
             <span className="mt-1 block text-2xs text-slate-500 font-medium">
               ℹ️ {t('Use at least 8 characters.')}
             </span>
           )}
         </label>

         <button
           type="submit"
           disabled={busy}
           className="mt-2 w-full rounded-xl bg-emerald-700 px-4 py-3.5 font-bold text-white shadow-sm hover:bg-emerald-800 disabled:opacity-60 transition-colors"
         >
           {busy ? t('Please wait…') : t(register ? 'Create account' : 'Log in')}
         </button>
       </form>

       {/* Bottom Toggle Prompt */}
       <p className="mt-6 text-center text-xs text-slate-600">
         {t(register ? 'Already have an account?' : 'New to AgriSmart AI?')}{' '}
         <button
           type="button"
           className="font-bold text-emerald-700 underline hover:text-emerald-900 ml-1"
           onClick={() => switchMode(register ? 'login' : 'register')}
         >
           {t(register ? 'Log in' : 'Create account')}
         </button>
       </p>

       <p className="mt-4 text-center text-2xs text-slate-400">
         🔒 {t('Your prediction history is private to your account.')}
       </p>
     </section>
   </main>
 );
}

function WeatherAdvice({weather,language}) {
 const advice=[];
 const rain=Number(weather.daily?.precipitation_probability_max?.[0] ?? 0);
 const wind=Number(weather.current?.wind_speed_10m ?? 0);
 const temp=Number(weather.current?.temperature_2m ?? 0);
 const humidity=Number(weather.current?.relative_humidity_2m ?? 0);
 if(rain>=60) advice.push(['Rain forecast is high. If the field soil is already wet, postpone irrigation and check drainage.','వర్ష సూచన ఎక్కువగా ఉంది. పొలం నేల ఇప్పటికే తడిగా ఉంటే నీటిపారుదల వాయిదా వేసి నీరు బయటకు వెళ్లే మార్గాలను పరిశీలించండి.','बारिश की संभावना अधिक है। खेत की मिट्टी पहले से गीली हो तो सिंचाई टालें और जल निकासी जाँचें।']);
 if(wind>=25) advice.push(['Wind is strong. Avoid spraying during strong winds to reduce spray drift.','గాలి వేగంగా ఉంది. మందు ఇతర ప్రాంతాలకు వెళ్లకుండా బలమైన గాలిలో పిచికారీ చేయవద్దు.','हवा तेज़ है। दवा के बहाव को रोकने के लिए तेज़ हवा में छिड़काव न करें।']);
 if(temp>=35) advice.push(['Temperature is high. Check crop moisture and follow crop-specific heat-stress guidance.','ఉష్ణోగ్రత ఎక్కువగా ఉంది. పంటలో తేమను పరిశీలించి, పంటకు సంబంధించిన వేడి ఒత్తిడి సూచనలు పాటించండి.','तापमान अधिक है। फसल में नमी जाँचें और फसल के अनुसार गर्मी से बचाव की सलाह अपनाएँ।']);
 if(humidity>=85) advice.push(['Humidity is high. Monitor the crop for fungal symptoms; humidity alone does not confirm disease.','గాలిలో తేమ ఎక్కువగా ఉంది. శిలీంధ్ర లక్షణాల కోసం పంటను గమనించండి; తేమ ఎక్కువగా ఉండటం మాత్రమే వ్యాధి నిర్ధారణ కాదు.','नमी अधिक है। फसल में फफूंद के लक्षण देखें; केवल अधिक नमी से रोग की पुष्टि नहीं होती।']);
 if(!advice.length) advice.push(['No major weather alert from these simple thresholds. Continue monitoring local conditions and crop stage.','ఈ సాధారణ పరిమితుల ప్రకారం పెద్ద వాతావరణ హెచ్చరిక లేదు. స్థానిక పరిస్థితులు మరియు పంట దశను గమనిస్తూ ఉండండి.','इन सामान्य सीमाओं के अनुसार कोई बड़ी मौसम चेतावनी नहीं है। स्थानीय स्थिति और फसल की अवस्था देखते रहें।']);
 return <section className="mt-5 rounded-2xl border border-emerald-100 bg-emerald-50 p-5"><h3 className="font-bold text-emerald-950">{translate('Weather-based advice',language)}</h3><ul className="mt-3 list-disc space-y-2 pl-5 text-sm text-emerald-950">{advice.map((a,i)=><li key={i}>{language==='te'?a[1]:language==='hi'?a[2]:a[0]}</li>)}</ul><p className="mt-3 text-xs text-emerald-800">{translate('Decision-support only. Verify advice with local agricultural experts.',language)}</p></section>;
}

export default App
