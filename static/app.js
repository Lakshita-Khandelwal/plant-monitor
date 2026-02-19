// Global variables
let supabase = null

const logsContainer = document.getElementById('logs-container')
const loading = document.getElementById('loading')
const emptyState = document.getElementById('empty-state')

// Function to get moisture level color and status
function getMoistureStatus(moisture) {
    const level = parseFloat(moisture)
    if (level < 30) return { color: 'red', status: 'Low - Needs Water', gradient: 'from-red-400 to-red-600' }
    if (level < 60) return { color: 'yellow', status: 'Medium', gradient: 'from-yellow-400 to-yellow-600' }
    return { color: 'green', status: 'Optimal', gradient: 'from-green-400 to-green-600' }
}

// Function to get light level color and status
function getLightStatus(light) {
    const level = parseFloat(light)
    if (level < 500) return { color: 'red', status: 'Low Light', icon: '🌑' }
    if (level < 1000) return { color: 'yellow', status: 'Medium Light', icon: '🌤️' }
    return { color: 'green', status: 'Bright Light', icon: '☀️' }
}

// Function to format timestamp
function formatTime(timestamp) {
    const date = new Date(timestamp)
    return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    })
}

// Create a card for each plant log
function createPlantCard(log) {
    const moistureInfo = getMoistureStatus(log.moisture)
    const lightInfo = getLightStatus(log.light || '0')
    
    const card = document.createElement('div')
    card.id = `log-${log.id}`
    card.className = 'bg-white rounded-2xl shadow-xl overflow-hidden fade-in hover:shadow-2xl transition-shadow duration-300'
    
    card.innerHTML = `
        <div class="md:flex">
            <!-- Image Section -->
            <div class="md:w-1/3 relative">
                <img src="${log.image_url}" 
                     alt="Plant photo" 
                     class="w-full h-64 md:h-full object-cover"
                     onerror="this.src='https://via.placeholder.com/400x400?text=Image+Not+Found'">
                <div class="absolute top-4 right-4 bg-white/90 backdrop-blur px-3 py-1 rounded-full text-sm font-semibold">
                    📸 ${formatTime(log.created_at)}
                </div>
            </div>
            
            <!-- Content Section -->
            <div class="md:w-2/3 p-8">
                <!-- Sensor Data Grid -->
                <div class="grid md:grid-cols-2 gap-6 mb-6">
                    <!-- Moisture Level -->
                    <div>
                        <div class="flex items-center justify-between mb-2">
                            <h3 class="text-lg font-semibold text-gray-700">Soil Moisture</h3>
                            <span class="text-2xl font-bold text-${moistureInfo.color}-600">${log.moisture}%</span>
                        </div>
                        
                        <!-- Progress Bar -->
                        <div class="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
                            <div class="moisture-bar h-full bg-gradient-to-r ${moistureInfo.gradient} rounded-full" 
                                 style="width: ${log.moisture}%"></div>
                        </div>
                        <p class="text-sm text-gray-500 mt-1">Status: ${moistureInfo.status}</p>
                    </div>

                    <!-- Light Level -->
                    <div>
                        <div class="flex items-center justify-between mb-2">
                            <h3 class="text-lg font-semibold text-gray-700">Light Level</h3>
                            <span class="text-2xl font-bold text-${lightInfo.color}-600">${log.light || 'N/A'} lux</span>
                        </div>
                        
                        <div class="bg-${lightInfo.color}-100 rounded-lg px-4 py-2 text-center">
                            <p class="text-sm font-medium text-${lightInfo.color}-800">${lightInfo.status}</p>
                        </div>
                    </div>
                </div>

                <!-- AI Analysis -->
                <div class="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-5 border border-purple-100">
                    <div class="flex items-center gap-2 mb-3">
                        <h3 class="text-lg font-semibold text-purple-900">Claude AI Analysis</h3>
                    </div>
                    <p class="text-gray-700 leading-relaxed whitespace-pre-line">${log.claude_advice}</p>
                </div>
            </div>
        </div>
    `
    
    return card
}

// Update UI with plant data
function updateUI(log) {
    loading.classList.add('hidden')
    emptyState.classList.add('hidden')
    
    // Check if card already exists (avoid duplicates)
    const existingCard = document.getElementById(`log-${log.id}`)
    if (existingCard) return
    
    const card = createPlantCard(log)
    logsContainer.insertBefore(card, logsContainer.firstChild)
}

// Load initial data
async function loadInitialData() {
    try {
        const { data, error } = await supabase
            .from('plant_logs')
            .select('*')
            .order('created_at', { ascending: false })
            .limit(20)
        
        loading.classList.add('hidden')
        
        if (error) throw error
        
        if (data && data.length > 0) {
            data.forEach(log => updateUI(log))
        } else {
            emptyState.classList.remove('hidden')
        }
    } catch (error) {
        console.error('Error loading data:', error)
        loading.innerHTML = `
            <div class="text-red-600">
                <p class="text-xl font-semibold">❌ Error loading data</p>
                <p class="text-sm mt-2">${error.message}</p>
            </div>
        `
    }
}

// Setup realtime subscription
function setupRealtimeSubscription() {
    const channel = supabase
        .channel('schema-db-changes')
        .on(
            'postgres_changes',
            { event: 'INSERT', schema: 'public', table: 'plant_logs' },
            (payload) => {
                console.log('🌱 New plant data received!', payload.new)
                updateUI(payload.new)
                
                // Show notification
                showNotification('New plant update received!')
            }
        )
        .subscribe()
    
    console.log('🌱 Realtime subscription active!')
}

// Optional: Show browser notification
function showNotification(message) {
    // Create toast notification
    const toast = document.createElement('div')
    toast.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg fade-in z-50'
    toast.innerHTML = `
        <div class="flex items-center gap-2">
            <span class="text-xl">🌱</span>
            <span class="font-medium">${message}</span>
        </div>
    `
    document.body.appendChild(toast)
    
    setTimeout(() => {
        toast.style.opacity = '0'
        setTimeout(() => toast.remove(), 300)
    }, 3000)
}

// Initialize the application
async function initApp() {
    try {
        console.log('🔧 Fetching Supabase configuration...')
        
        // Fetch Supabase config from backend
        const response = await fetch('/config')
        if (!response.ok) {
            throw new Error('Failed to fetch configuration')
        }
        
        const config = await response.json()
        console.log('✅ Configuration loaded successfully')
        
        // Initialize Supabase client
        supabase = window.supabase.createClient(config.supabaseUrl, config.supabaseAnonKey)
        console.log('✅ Supabase client initialized')
        
        // Load initial data
        await loadInitialData()
        
        // Setup realtime subscription
        setupRealtimeSubscription()
        
        console.log('🌱 Plant Monitor initialized and listening for updates!')
        
    } catch (error) {
        console.error('❌ Initialization error:', error)
        loading.innerHTML = `
            <div class="text-red-600">
                <p class="text-xl font-semibold">❌ Failed to initialize app</p>
                <p class="text-sm mt-2">${error.message}</p>
                <p class="text-sm mt-2">Make sure the server is running and .env is configured.</p>
            </div>
        `
    }
}

// Start the app when DOM is ready
initApp()
