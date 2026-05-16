let selectedFilePath = null;
let analysisResults = null;

// File selection button
document.getElementById('selectBtn').addEventListener('click', async () => {
  const filePath = await window.electronAPI.selectFile();
  if (filePath) {
    selectedFilePath = filePath;
    const fileName = filePath.split(/[\\\\\\//]/).pop();
    
    const fileInfo = document.getElementById('fileInfo');
    fileInfo.innerHTML = `<strong>✅ فایل انتخاب شده:</strong> ${fileName}`;
    fileInfo.classList.add('show');
    
    document.getElementById('analysisSection').style.display = 'block';
    document.getElementById('analyzeBtn').disabled = false;
  }
});

// Analyze button
document.getElementById('analyzeBtn').addEventListener('click', async () => {
  if (!selectedFilePath) return;
  
  const analyzeBtn = document.getElementById('analyzeBtn');
  const analyzeText = document.getElementById('analyzeText');
  const spinner = document.getElementById('spinner');
  const status = document.getElementById('status');
  
  analyzeBtn.disabled = true;
  analyzeText.style.display = 'none';
  spinner.style.display = 'inline-block';
  
  status.innerHTML = '⏳ درحال تحلیل... این عملیات ممکن است چند دقیقه طول بکشد';
  status.classList.remove('error');
  status.classList.add('loading', 'show');
  
  try {
    analysisResults = await window.electronAPI.analyzeCSV(selectedFilePath);
    
    if (analysisResults.status === 'success') {
      status.innerHTML = '✅ تحلیل با موفقیت انجام شد!';
      status.classList.remove('loading');
      status.classList.add('success');
      
      // Show results
      document.getElementById('resultsSection').style.display = 'block';
      
      if (analysisResults.volume_file) {
        document.getElementById('volumeCard').style.display = 'block';
        document.getElementById('volumeCard').dataset.path = analysisResults.volume_file;
      }
      
      if (analysisResults.gradient_file) {
        document.getElementById('gradientCard').style.display = 'block';
        document.getElementById('gradientCard').dataset.path = analysisResults.gradient_file;
      }
    } else {
      status.innerHTML = `❌ خطا: ${analysisResults.message}`;
      status.classList.remove('loading');
      status.classList.add('error');
    }
  } catch (error) {
    status.innerHTML = `❌ خطا در تحلیل: ${error.message}`;
    status.classList.remove('loading');
    status.classList.add('error');
  } finally {
    analyzeBtn.disabled = false;
    analyzeText.style.display = 'inline';
    spinner.style.display = 'none';
  }
});

// Open volume tomography
window.openVolume = async function() {
  const card = document.getElementById('volumeCard');
  const filePath = card.dataset.path;
  if (filePath) {
    await window.electronAPI.openFile(filePath);
  }
};

// Open gradient tomography
window.openGradient = async function() {
  const card = document.getElementById('gradientCard');
  const filePath = card.dataset.path;
  if (filePath) {
    await window.electronAPI.openFile(filePath);
  }
};
