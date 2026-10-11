import os

os.makedirs('templates/classes', exist_ok=True)

# 1. templates/classes/student_hub.html
student_hub = """{% extends 'base.html' %}
{% load static %}

{% block content %}
<style>
    :root {
        --cinema-bg: #07090e;
        --cinema-surface: rgba(15, 23, 42, 0.78);
        --cinema-border: rgba(255, 255, 255, 0.12);
        --cinema-purple: #c084fc;
        --cinema-text-main: #ffffff;
        --cinema-text-sub: #e2e8f0;
        --cinema-text-body: #cbd5e1;
    }

    body {
        background-color: var(--cinema-bg);
    }

    .cinema-hero-banner {
        background: radial-gradient(circle at 85% 15%, rgba(192, 132, 252, 0.22) 0%, transparent 50%),
                    radial-gradient(circle at 15% 85%, rgba(56, 189, 248, 0.18) 0%, transparent 55%),
                    linear-gradient(135deg, #090d16 0%, #0f172a 100%);
        border: 1px solid var(--cinema-border);
        border-radius: 24px;
        box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.7), inset 0 1px 0 rgba(255, 255, 255, 0.15);
        position: relative;
        overflow: hidden;
    }

    .class-quantum-card {
        background: var(--cinema-surface);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        border: 1px solid var(--cinema-border);
        border-radius: 20px;
        transition: transform 0.28s cubic-bezier(0.16, 1, 0.3, 1),
                    border-color 0.28s ease,
                    box-shadow 0.28s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .class-quantum-card:hover {
        transform: translateY(-6px);
        border-color: rgba(192, 132, 252, 0.55);
        box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.7), 0 0 25px rgba(192, 132, 252, 0.25);
    }

    .omni-search-wrapper {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid var(--cinema-border);
        border-radius: 9999px;
        backdrop-filter: blur(12px);
        transition: all 0.25s ease;
    }

    .omni-search-wrapper:focus-within {
        border-color: var(--cinema-purple);
        box-shadow: 0 0 0 4px rgba(192, 132, 252, 0.2);
    }

    .omni-search-input {
        background: transparent;
        border: none;
        color: #ffffff;
        outline: none;
    }

    .omni-search-input::placeholder {
        color: #94a3b8;
    }

    .filter-chip {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.12);
        color: #cbd5e1;
        border-radius: 9999px;
        padding: 8px 18px;
        font-size: 0.85rem;
        font-weight: 600;
        transition: all 0.2s ease;
        cursor: pointer;
        user-select: none;
        white-space: nowrap;
    }

    .filter-chip:hover {
        background: rgba(255, 255, 255, 0.1);
        color: #ffffff;
        border-color: rgba(255, 255, 255, 0.25);
    }

    .filter-chip.active {
        background: linear-gradient(135deg, rgba(192, 132, 252, 0.25), rgba(56, 189, 248, 0.25));
        color: #c084fc;
        border-color: var(--cinema-purple);
        box-shadow: 0 0 15px rgba(192, 132, 252, 0.25);
    }

    .btn-play-class {
        background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
        border: 1px solid rgba(255, 255, 255, 0.18);
        color: #ffffff !important;
        font-weight: 700;
        letter-spacing: 0.03em;
        transition: all 0.25s ease;
    }

    .btn-play-class:hover {
        background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
        box-shadow: 0 0 25px rgba(139, 92, 246, 0.5);
        transform: scale(1.02);
    }

    .telemetry-dot-purple {
        width: 8px;
        height: 8px;
        background-color: #c084fc;
        border-radius: 50%;
        box-shadow: 0 0 10px #c084fc;
        animation: pulse-dot 2s infinite ease-in-out;
    }

    @keyframes pulse-dot {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(1.25); }
    }
</style>

<div class="container py-4 py-md-5">

    <!-- 1. HERO OPERATIVO BANNER -->
    <div class="card p-4 p-md-5 mb-4 cinema-hero-banner text-white">
        <div class="d-flex flex-column flex-lg-row justify-content-between align-items-lg-center gap-4 position-relative z-index-2">
            <div>
                <div class="d-flex align-items-center gap-2 mb-3">
                    <span class="telemetry-dot-purple"></span>
                    <span class="badge font-monospace text-uppercase" style="background: rgba(192, 132, 252, 0.12); color: #c084fc; border: 1px solid rgba(192, 132, 252, 0.35); padding: 6px 14px; border-radius: 9999px;">
                        <i class="fas fa-play-circle me-1"></i> Streaming Académico Multidisciplinar
                    </span>
                    <span class="badge border font-monospace text-white" style="background: rgba(255,255,255,0.06); border-color: rgba(255,255,255,0.15) !important; padding: 6px 12px; border-radius: 9999px;">
                        Zero-Distractions
                    </span>
                </div>
                <h1 class="display-5 fw-black text-white mb-2 tracking-tight">Hub de Clases Magistrales</h1>
                <p class="mb-0 max-w-2xl" style="color: var(--cinema-text-sub); font-size: 1.05rem; line-height: 1.6;">
                    Aprende la teoría fundamental y avanza a tu propio ritmo con lecciones estructuradas por los docentes de Learning Labs.
                </p>
            </div>

            <div class="d-flex flex-column sm:flex-row align-items-stretch align-items-lg-center gap-3">
                <div class="border rounded-4 p-3 text-center d-flex align-items-center gap-3 px-4 shadow-sm" style="background: rgba(0, 0, 0, 0.5); border-color: rgba(255,255,255,0.12) !important;">
                    <div class="text-start">
                        <small class="d-block font-monospace text-uppercase" style="font-size: 0.7rem; color: #94a3b8;">Catálogo Teórico</small>
                        <span class="h4 fw-black m-0 font-monospace" style="color: #c084fc;">{{ total_clases|default:'0' }}</span>
                        <span class="small text-white font-monospace"> Lecciones</span>
                    </div>
                </div>
                <a href="{% url 'dashboard_estudiante' %}" class="btn btn-outline-light rounded-pill px-4 py-3 d-inline-flex align-items-center justify-content-center gap-2 fw-semibold" style="border-color: rgba(255,255,255,0.25);">
                    <i class="fas fa-arrow-left"></i>
                    <span>Dashboard</span>
                </a>
            </div>
        </div>
    </div>

    <!-- 2. CONTROL HUB: BÚSQUEDA Y FILTROS POR MATERIA -->
    <div class="card border-0 rounded-4 p-3 mb-5 shadow-sm" style="background: rgba(15, 23, 42, 0.7); border: 1px solid var(--cinema-border) !important;">
        <div class="row g-3 align-items-center justify-content-between">
            <div class="col-12 col-lg-5">
                <div class="omni-search-wrapper d-flex align-items-center px-3 py-2">
                    <i class="fas fa-search me-2" style="color: #c084fc;"></i>
                    <input type="text" 
                           id="classSearchInput" 
                           class="omni-search-input w-100 font-sans text-sm" 
                           placeholder="Buscar por tema, concepto, método o materia..." 
                           autocomplete="off">
                    <button class="btn btn-sm p-0 d-none text-white-50" id="clearSearchBtn" onclick="clearSearch()" aria-label="Limpiar búsqueda">
                        <i class="fas fa-times-circle"></i>
                    </button>
                </div>
            </div>

            <div class="col-12 col-lg-7">
                <div class="d-flex align-items-center gap-2 overflow-x-auto pb-1 pb-lg-0 scrollbar-none" id="subjectFilterContainer">
                    <div class="filter-chip active" data-subject="ALL">Todas</div>
                    {% for subject_label, classes in classes_by_subject.items %}
                    <div class="filter-chip" data-subject="{{ subject_label|slugify }}">{{ subject_label }} ({{ classes|length }})</div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>

    <!-- 3. FEED DE CLASES POR MATERIA -->
    <div id="classesGrid">
        {% for subject_label, classes in classes_by_subject.items %}
        <div class="subject-section mb-5" data-subject-group="{{ subject_label|slugify }}">
            
            <div class="d-flex align-items-center justify-content-between mb-4 border-bottom pb-3" style="border-color: rgba(255, 255, 255, 0.1) !important;">
                <div class="d-flex align-items-center gap-3">
                    <div class="p-2 rounded-3" style="width: 44px; height: 44px; display: grid; place-items: center; background: rgba(192, 132, 252, 0.12); border: 1px solid rgba(192, 132, 252, 0.35); color: #c084fc;">
                        <i class="fas fa-graduation-cap fs-5"></i>
                    </div>
                    <div>
                        <h3 class="fw-bold text-white mb-0 fs-4">{{ subject_label }}</h3>
                        <small class="font-monospace" style="color: #94a3b8;">Ruta pedagógica estructurada</small>
                    </div>
                </div>
                <span class="badge rounded-pill border px-3 py-2 font-monospace text-white" style="background: rgba(255, 255, 255, 0.06); border-color: rgba(255, 255, 255, 0.12) !important;">
                    {{ classes|length }} lecciones
                </span>
            </div>

            <div class="row g-4">
                {% for c in classes %}
                <div class="col-12 col-md-6 col-lg-4 class-card-item" 
                     data-title="{{ c.title|lower }}" 
                     data-desc="{{ c.description|lower }}" 
                     data-subject="{{ subject_label|slugify }}">
                    <div class="card h-100 class-quantum-card d-flex flex-column position-relative">
                        <div class="card-body p-4 d-flex flex-column">
                            
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <span class="badge font-monospace border" style="background: rgba(192, 132, 252, 0.1); border-color: rgba(192, 132, 252, 0.3) !important; color: #c084fc; font-size: 0.75rem; padding: 5px 12px; border-radius: 9999px;">
                                    Lección #{{ c.order }}
                                </span>
                                <span class="badge font-monospace text-white border" style="background: rgba(255, 255, 255, 0.06); border-color: rgba(255, 255, 255, 0.12) !important; color: #e2e8f0 !important; font-size: 0.7rem; border-radius: 9999px;">
                                    <i class="fas fa-clock me-1 text-warning"></i> ~{{ c.duration_minutes }} min
                                </span>
                            </div>

                            <h5 class="fw-bold text-white mb-2 lh-base">{{ c.title }}</h5>
                            <p class="small flex-grow-1 mb-4" style="color: var(--cinema-text-body); font-size: 0.88rem; line-height: 1.65; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;">
                                {{ c.description }}
                            </p>

                            <div class="mt-auto pt-3 border-top" style="border-color: rgba(255, 255, 255, 0.08) !important;">
                                <a href="{% url 'class_player_view' c.uuid %}" 
                                   class="btn btn-play-class rounded-pill w-100 py-2 d-flex align-items-center justify-content-center gap-2 shadow-sm">
                                    <i class="fas fa-play fs-7"></i>
                                    <span>Ver Lección en Vivo</span>
                                </a>
                            </div>

                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% empty %}
        <div class="card border-0 rounded-4 p-5 text-center shadow-sm" style="background: rgba(15, 23, 42, 0.5); border: 1px solid var(--cinema-border) !important;">
            <div class="py-4">
                <i class="fas fa-film fa-4x mb-3" style="color: #c084fc; opacity: 0.6;"></i>
                <h4 class="fw-bold text-white">No hay clases registradas</h4>
                <p class="text-white-50 max-w-md mx-auto">El cuerpo académico publicará nuevas lecciones próximamente.</p>
            </div>
        </div>
        {% endfor %}
    </div>

    <!-- 4. ESTADO DE BÚSQUEDA SIN RESULTADOS -->
    <div id="searchNoResults" class="card border-0 rounded-4 p-5 text-center shadow-sm d-none mt-4" style="background: rgba(15, 23, 42, 0.5); border: 2px dashed rgba(255,255,255,0.15) !important;">
        <div class="py-4">
            <i class="fas fa-search-minus fa-3x mb-3 text-white-50"></i>
            <h4 class="fw-bold text-white">Sin lecciones coincidentes</h4>
            <p class="text-white-50 mb-3" id="searchFeedbackText">No encontramos clases que coincidan con tu término.</p>
            <button class="btn btn-outline-info rounded-pill px-4 btn-sm fw-semibold" onclick="clearSearch()">
                Restablecer Catálogo
            </button>
        </div>
    </div>

</div>

<script>
    document.addEventListener('DOMContentLoaded', () => {
        const searchInput = document.getElementById('classSearchInput');
        const clearBtn = document.getElementById('clearSearchBtn');
        const filterChips = document.querySelectorAll('.filter-chip');
        const cardItems = document.querySelectorAll('.class-card-item');
        const subjectSections = document.querySelectorAll('.subject-section');
        const noResultsAlert = document.getElementById('searchNoResults');
        const searchFeedbackText = document.getElementById('searchFeedbackText');

        let currentSubjectFilter = 'ALL';
        let currentSearchQuery = '';

        function applyFilters() {
            let visibleCount = 0;
            const query = currentSearchQuery.trim().toLowerCase();

            cardItems.forEach(card => {
                const title = card.getAttribute('data-title') || '';
                const desc = card.getAttribute('data-desc') || '';
                const subject = card.getAttribute('data-subject') || '';

                const matchesQuery = query === '' || title.includes(query) || desc.includes(query);
                const matchesSubject = currentSubjectFilter === 'ALL' || subject === currentSubjectFilter;

                if (matchesQuery && matchesSubject) {
                    card.style.display = '';
                    visibleCount++;
                } else {
                    card.style.display = 'none';
                }
            });

            subjectSections.forEach(section => {
                const visibleCards = section.querySelectorAll('.class-card-item:not([style*="display: none"])');
                if (visibleCards.length === 0) {
                    section.style.display = 'none';
                } else {
                    section.style.display = '';
                }
            });

            if (visibleCount === 0) {
                noResultsAlert.classList.remove('d-none');
                if (query !== '') {
                    searchFeedbackText.textContent = `No encontramos clases para "${currentSearchQuery}".`;
                } else {
                    searchFeedbackText.textContent = 'No hay clases activas en la materia seleccionada.';
                }
            } else {
                noResultsAlert.classList.add('d-none');
            }
        }

        let debounceTimer;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            currentSearchQuery = e.target.value;
            
            if (currentSearchQuery.length > 0) {
                clearBtn.classList.remove('d-none');
            } else {
                clearBtn.classList.add('d-none');
            }

            debounceTimer = setTimeout(applyFilters, 60);
        });

        filterChips.forEach(chip => {
            chip.addEventListener('click', () => {
                filterChips.forEach(c => c.classList.remove('active'));
                chip.classList.add('active');
                currentSubjectFilter = chip.getAttribute('data-subject');
                applyFilters();
            });
        });

        window.clearSearch = function() {
            searchInput.value = '';
            currentSearchQuery = '';
            clearBtn.classList.add('d-none');
            applyFilters();
            searchInput.focus();
        };
    });
</script>
{% endblock %}
"""

# 2. templates/classes/player.html
player = """{% extends 'base.html' %}
{% load static %}

{% block content %}
<style>
    :root {
        --cinema-player-bg: #05070d;
        --cinema-hud-bg: rgba(11, 15, 25, 0.95);
        --cinema-border: rgba(255, 255, 255, 0.12);
        --cinema-purple: #c084fc;
    }

    body {
        background-color: var(--cinema-player-bg);
    }

    .theater-container {
        min-height: calc(100vh - 75px);
        display: flex;
        flex-direction: column;
    }

    .theater-hud {
        background: var(--cinema-hud-bg);
        backdrop-filter: blur(20px);
        border: 1px solid var(--cinema-border);
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
        z-index: 20;
    }

    .video-viewport-wrapper {
        background: #000000;
        border: 1px solid var(--cinema-border);
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.8);
        position: relative;
    }

    .native-cinema-video {
        width: 100%;
        height: 100%;
        max-height: 72vh;
        background: #000;
        outline: none;
    }

    .syllabus-sidebar {
        background: rgba(15, 23, 42, 0.75);
        backdrop-filter: blur(18px);
        border: 1px solid var(--cinema-border);
        border-radius: 20px;
        max-height: 72vh;
        display: flex;
        flex-direction: column;
    }

    .syllabus-item {
        padding: 12px 16px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        transition: all 0.2s ease;
        text-decoration: none;
        display: block;
    }

    .syllabus-item:hover {
        background: rgba(255, 255, 255, 0.05);
    }

    .syllabus-item.active {
        background: rgba(192, 132, 252, 0.15);
        border-left: 3px solid var(--cinema-purple);
    }
</style>

<div class="container-fluid px-3 py-3 theater-container">
    
    <!-- 1. HUD SUPERIOR -->
    <div class="theater-hud py-2 px-3 px-md-4 mb-3 d-flex flex-wrap justify-content-between align-items-center gap-2">
        <div class="d-flex align-items-center gap-3">
            <a href="{% url 'student_classes_hub' %}" class="btn btn-outline-light btn-sm rounded-pill px-3 d-inline-flex align-items-center gap-2">
                <i class="fas fa-chevron-left" style="color: var(--cinema-purple);"></i>
                <span class="d-none d-sm-inline">Hub de Clases</span>
            </a>
            
            <div class="d-flex align-items-center gap-2 border-start border-secondary border-opacity-25 ps-3">
                <span class="badge rounded-pill font-monospace" style="background: rgba(192, 132, 252, 0.2); color: var(--cinema-purple); border: 1px solid rgba(192, 132, 252, 0.4);">
                    {{ current_class.get_subject_display }}
                </span>
                <span class="fw-bold text-white fs-6 d-none d-md-inline text-truncate" style="max-width: 380px;" title="{{ current_class.title }}">
                    {{ current_class.title }}
                </span>
            </div>
        </div>

        <div class="d-flex align-items-center gap-2 ms-auto">
            <!-- Selector de Velocidad -->
            <div class="btn-group btn-group-sm">
                <button class="btn btn-dark border border-secondary text-white-50 px-2" onclick="changeSpeed(1)">1x</button>
                <button class="btn btn-dark border border-secondary text-white-50 px-2" onclick="changeSpeed(1.25)">1.25x</button>
                <button class="btn btn-dark border border-secondary text-white-50 px-2" onclick="changeSpeed(1.5)">1.5x</button>
                <button class="btn btn-dark border border-secondary text-white-50 px-2" onclick="changeSpeed(2)">2x</button>
            </div>

            <!-- Pantalla Completa -->
            <button onclick="toggleVideoFullscreen()" class="btn btn-primary btn-sm rounded-pill px-3 d-inline-flex align-items-center gap-2 fw-semibold" style="background: #7c3aed; border-color: #7c3aed;">
                <i class="fas fa-expand"></i>
                <span class="d-none d-sm-inline">Pantalla Completa</span>
            </button>
        </div>
    </div>

    <!-- 2. REPRODUCTOR Y SYLLABUS -->
    <div class="row g-3 flex-grow-1">
        <!-- Viewport del Video -->
        <div class="col-12 col-xl-9">
            <div class="video-viewport-wrapper h-100 d-flex flex-column">
                <video id="theaterVideo" 
                       class="native-cinema-video flex-grow-1" 
                       controls 
                       autoplay 
                       playsinline
                       preload="metadata">
                    <source src="{{ current_class.video_url }}" type="video/mp4">
                    Tu navegador no soporta el formato de video HTML5.
                </video>
                
                <div class="p-3 text-white border-top border-secondary border-opacity-25" style="background: rgba(15, 23, 42, 0.9);">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h5 class="fw-bold text-white mb-1">{{ current_class.title }}</h5>
                            <p class="text-white-50 small mb-0" style="line-height: 1.6;">{{ current_class.description }}</p>
                        </div>
                        <span class="badge bg-dark border text-muted font-monospace small ms-3">
                            Secuencia #{{ current_class.order }}
                        </span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Sidebar Syllabus de la Materia -->
        <div class="col-12 col-xl-3">
            <div class="syllabus-sidebar h-100">
                <div class="p-3 border-bottom border-secondary border-opacity-25 d-flex justify-content-between align-items-center">
                    <h6 class="fw-bold text-white mb-0 font-monospace small text-uppercase">
                        <i class="fas fa-list-ol text-purple me-1" style="color: var(--cinema-purple);"></i> Programa del Módulo
                    </h6>
                    <span class="badge bg-dark text-muted font-monospace" style="font-size: 0.7rem;">{{ playlist|length }} Clases</span>
                </div>

                <div class="overflow-y-auto flex-grow-1 scrollbar-none">
                    {% for item in playlist %}
                    <a href="{% url 'class_player_view' item.uuid %}" 
                       class="syllabus-item {% if item.uuid == current_class.uuid %}active{% endif %}">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <span class="badge rounded-pill font-monospace" style="font-size: 0.65rem; background: rgba(255,255,255,0.08); color: #cbd5e1;">
                                Lección #{{ item.order }}
                            </span>
                            <small class="text-muted font-monospace" style="font-size: 0.7rem;">{{ item.duration_minutes }}m</small>
                        </div>
                        <span class="small fw-semibold d-block text-truncate {% if item.uuid == current_class.uuid %}text-white{% else %}text-white-50{% endif %}" title="{{ item.title }}">
                            {{ item.title }}
                        </span>
                    </a>
                    {% endfor %}
                </div>

                <div class="p-2 border-top border-secondary border-opacity-25 text-center text-muted font-monospace small" style="font-size: 0.7rem;">
                    <i class="fas fa-shield-alt text-success me-1"></i> Contenido encapsulado en Learning Labs
                </div>
            </div>
        </div>
    </div>

</div>

<script>
    const video = document.getElementById('theaterVideo');

    function changeSpeed(val) {
        if (video) video.playbackRate = val;
    }

    function toggleVideoFullscreen() {
        if (!document.fullscreenElement) {
            if (video.requestFullscreen) video.requestFullscreen();
            else if (video.webkitRequestFullscreen) video.webkitRequestFullscreen();
        } else {
            if (document.exitFullscreen) document.exitFullscreen();
        }
    }

    document.addEventListener('keydown', (e) => {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

        if (e.code === 'Space') {
            e.preventDefault();
            if (video.paused) video.play();
            else video.pause();
        }
        if (e.code === 'ArrowRight') {
            e.preventDefault();
            video.currentTime += 5;
        }
        if (e.code === 'ArrowLeft') {
            e.preventDefault();
            video.currentTime -= 5;
        }
        if (e.key === 'f' || e.key === 'F') {
            e.preventDefault();
            toggleVideoFullscreen();
        }
    });
</script>
{% endblock %}
"""

# 3. templates/classes/admin_manage.html
admin_manage = """{% extends 'base.html' %}
{% load static %}

{% block content %}
<div class="container-fluid px-4 py-4 max-w-7xl">
    
    <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3 mb-4">
        <div>
            <div class="d-flex align-items-center gap-2 mb-1">
                <span class="badge bg-purple bg-opacity-10 text-purple border border-purple border-opacity-25 rounded-pill px-3 py-1 font-monospace small" style="background: rgba(192,132,252,0.1); color: #7c3aed;">
                    <i class="fas fa-video me-1"></i> Media Engine
                </span>
                <span class="badge bg-light text-muted border rounded-pill small font-monospace">Administración Académica</span>
            </div>
            <h1 class="h3 fw-black text-dark mb-0 tracking-tight">Gestor Institucional de Clases Magistrales</h1>
            <p class="text-muted small mb-0">Carga, organización por disciplina y disponibilidad para los estudiantes.</p>
        </div>
        
        <div class="d-flex align-items-center gap-2">
            <a href="{% url 'admin_dashboard' %}" class="btn btn-outline-secondary rounded-pill px-3 py-2 d-inline-flex align-items-center gap-2 fw-semibold">
                <i class="fas fa-arrow-left"></i>
                <span>Dashboard Admin</span>
            </a>
            <a href="{% url 'student_classes_hub' %}" target="_blank" class="btn btn-dark rounded-pill px-3 py-2 d-inline-flex align-items-center gap-2 fw-semibold shadow-sm">
                <i class="fas fa-eye text-info"></i>
                <span>Vista Estudiante</span>
            </a>
        </div>
    </div>

    <div class="row g-4">
        <!-- Formulario -->
        <div class="col-12 col-xl-5">
            <div class="card border-0 shadow-sm p-4 rounded-4 bg-white position-sticky" style="top: 2rem;">
                <h5 class="fw-bold text-dark mb-3 d-flex align-items-center gap-2">
                    <i class="fas fa-cloud-upload-alt text-primary"></i> Publicar Nueva Clase
                </h5>

                <form method="POST" novalidate>
                    {% csrf_token %}
                    
                    <div class="mb-3">
                        <label class="form-label fw-bold small text-muted text-uppercase">Título de la Lección</label>
                        {{ form.title }}
                        {% if form.title.errors %}<div class="text-danger small mt-1 font-monospace">{{ form.title.errors.0 }}</div>{% endif %}
                    </div>

                    <div class="mb-3">
                        <label class="form-label fw-bold small text-muted text-uppercase">Materia / Disciplina</label>
                        {{ form.subject }}
                        {% if form.subject.errors %}<div class="text-danger small mt-1 font-monospace">{{ form.subject.errors.0 }}</div>{% endif %}
                    </div>

                    <div class="mb-3">
                        <label class="form-label fw-bold small text-muted text-uppercase">Descripción Temática</label>
                        {{ form.description }}
                        {% if form.description.errors %}<div class="text-danger small mt-1 font-monospace">{{ form.description.errors.0 }}</div>{% endif %}
                    </div>

                    <div class="mb-3">
                        <label class="form-label fw-bold small text-muted text-uppercase">URL Directa del Video (HTTPS / CDN / R2)</label>
                        {{ form.video_url }}
                        <small class="text-muted d-block mt-1 font-monospace" style="font-size: 0.72rem;">
                            <i class="fas fa-lock text-success me-1"></i> Acepta Cloudflare R2, Cloudinary o cualquier URL directa en .mp4
                        </small>
                        {% if form.video_url.errors %}<div class="text-danger small mt-1 font-monospace">{{ form.video_url.errors.0 }}</div>{% endif %}
                    </div>

                    <div class="row g-3 mb-4">
                        <div class="col-4">
                            <label class="form-label fw-bold small text-muted text-uppercase">Duración (min)</label>
                            {{ form.duration_minutes }}
                        </div>
                        <div class="col-4">
                            <label class="form-label fw-bold small text-muted text-uppercase">Orden</label>
                            {{ form.order }}
                        </div>
                        <div class="col-4 pt-4 d-flex align-items-center">
                            <span class="small fw-bold text-dark me-2">Visible:</span>
                            {{ form.is_active }}
                        </div>
                    </div>

                    <button type="submit" class="btn btn-primary w-100 rounded-pill py-2 fw-bold d-flex align-items-center justify-content-center gap-2 shadow-sm">
                        <i class="fas fa-check-circle"></i>
                        <span>Guardar y Publicar</span>
                    </button>
                </form>
            </div>
        </div>

        <!-- Tabla -->
        <div class="col-12 col-xl-7">
            <div class="card border-0 shadow-sm p-4 rounded-4 bg-white">
                <div class="d-flex justify-content-between align-items-center mb-3 pb-2 border-bottom">
                    <div>
                        <h5 class="fw-bold text-dark mb-0">Catálogo Registrado</h5>
                        <small class="text-muted font-monospace">Total: {{ total_registros }} lecciones</small>
                    </div>
                </div>

                <div class="table-responsive">
                    <table class="table align-middle w-100">
                        <thead class="table-light">
                            <tr>
                                <th>Ord</th>
                                <th>Título</th>
                                <th>Materia</th>
                                <th>Estado</th>
                                <th class="text-end">Acción</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for c in classes %}
                            <tr>
                                <td class="font-monospace text-muted fw-bold">#{{ c.order }}</td>
                                <td>
                                    <div class="fw-bold text-dark text-truncate" style="max-width: 220px;" title="{{ c.title }}">{{ c.title }}</div>
                                    <small class="text-muted font-monospace">{{ c.duration_minutes }} min</small>
                                </td>
                                <td>
                                    <span class="badge bg-primary bg-opacity-10 text-primary border rounded-pill font-monospace small">
                                        {{ c.get_subject_display }}
                                    </span>
                                </td>
                                <td>
                                    {% if c.is_active %}
                                        <span class="badge bg-success bg-opacity-10 text-success rounded-pill px-2 py-1 small">Activo</span>
                                    {% else %}
                                        <span class="badge bg-secondary bg-opacity-10 text-secondary rounded-pill px-2 py-1 small">Oculto</span>
                                    {% endif %}
                                </td>
                                <td class="text-end">
                                    <a href="{% url 'class_player_view' c.uuid %}" target="_blank" class="btn btn-sm btn-light rounded-circle text-primary me-1" title="Probar reproducción">
                                        <i class="fas fa-play"></i>
                                    </a>
                                    <form method="POST" action="{% url 'admin_class_delete' c.uuid %}" class="d-inline" onsubmit="return confirm('¿Seguro que deseas eliminar esta clase?');">
                                        {% csrf_token %}
                                        <button type="submit" class="btn btn-sm btn-light rounded-circle text-danger" title="Eliminar">
                                            <i class="fas fa-trash-alt"></i>
                                        </button>
                                    </form>
                                </td>
                            </tr>
                            {% empty %}
                            <tr>
                                <td colspan="5" class="text-center text-muted py-5">No hay clases registradas en la base de datos.</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>

                {% if page_obj.has_other_pages %}
                <div class="d-flex justify-content-center pt-3 border-top mt-2">
                    <ul class="pagination pagination-sm mb-0">
                        {% if page_obj.has_previous %}
                            <li class="page-item"><a class="page-link" href="?page={{ page_obj.previous_page_number }}">Anterior</a></li>
                        {% endif %}
                        <li class="page-item active"><span class="page-link">{{ page_obj.number }} de {{ page_obj.paginator.num_pages }}</span></li>
                        {% if page_obj.has_next %}
                            <li class="page-item"><a class="page-link" href="?page={{ page_obj.next_page_number }}">Siguiente</a></li>
                        {% endif %}
                    </ul>
                </div>
                {% endif %}

            </div>
        </div>
    </div>

</div>
{% endblock %}
"""

with open('templates/classes/student_hub.html', 'w', encoding='utf-8') as f:
    f.write(student_hub)
with open('templates/classes/player.html', 'w', encoding='utf-8') as f:
    f.write(player)
with open('templates/classes/admin_manage.html', 'w', encoding='utf-8') as f:
    f.write(admin_manage)

print("¡Los 3 templates de Clases Magistrales fueron creados exitosamente!")
