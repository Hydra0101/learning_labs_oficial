# ===================================================================
# tasks/forms.py (COMPLETO, CORREGIDO Y BLINDADO)
# ===================================================================

from .models import ActaInstitucional
from django import forms # 💡 CRÍTICO: Asegura la importación base de forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm 
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import update_session_auth_hash
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
import unicodedata
from urllib.parse import urlparse
from .models import Simulator, MasterClass

# Importamos TODOS los modelos necesarios

from .models import (
    Question, Answer, ROLES_CHOICES, Observacion, Periodo, Matricula,
    MensajeInterno, Acudiente, Curso, AsignacionMateria,
    Post, Comment, SocialGroup, Perfil, Seguimiento, MasterClass  # Aseguramos Perfil
)

# Definición del modelo User de forma segura
User = get_user_model() 

# 🛡️ IMPORTACIÓN DE SEGURIDAD (Desde tu nuevo utils.py)
# Asumo que la función validar_lenguaje_apropiado existe en .utils
try:
    from .utils import validar_lenguaje_apropiado
except ImportError:
    def validar_lenguaje_apropiado(texto):
        return True

# ===================================================================
# 🛡️ MIXIN DE SEGURIDAD (DRY: Don't Repeat Yourself)
# ===================================================================
class ContentSecurityMixin:
    """
    Mixin para validar lenguaje apropiado en campos de texto.
    Se inyecta en cualquier formulario que necesite filtrar groserías.
    """
    def validar_contenido_seguro(self, contenido, campo_nombre):
        # Nota: Asumo que validar_lenguaje_apropiado es una función válida
        if contenido and not validar_lenguaje_apropiado(contenido):
            raise ValidationError(
                f"El contenido del campo '{campo_nombre}' infringe las normas de convivencia escolar. "
                "Por favor, revisa tu lenguaje."
            )
        return contenido

# ===================================================================
# FORMULARIOS DEL FORO (BLINDADOS)
# ===================================================================

class QuestionForm(forms.ModelForm, ContentSecurityMixin):
    """Formulario para crear o editar una pregunta en el foro."""
    class Meta:
        model = Question
        fields = ['title', 'content']

    def clean_title(self):
        return self.validar_contenido_seguro(self.cleaned_data.get('title'), 'Título')

    def clean_content(self):
        return self.validar_contenido_seguro(self.cleaned_data.get('content'), 'Contenido')

class AnswerForm(forms.ModelForm, ContentSecurityMixin):
    """Formulario para publicar una respuesta a una pregunta."""
    class Meta:
        model = Answer
        fields = ['content']

    def clean_content(self):
        return self.validar_contenido_seguro(self.cleaned_data.get('content'), 'Respuesta')

# ===================================================================
# 🏗️ FORMULARIOS SOCIALES (FEED & GRUPOS)
# ===================================================================

# tasks/forms.py

class PostForm(forms.ModelForm, ContentSecurityMixin):
    """
    Formulario para crear publicaciones en el muro social.
    Incluye campos para contenido de texto, imagen y archivo adjunto,
    así como validación de lenguaje inapropiado (ContentSecurityMixin).
    """
    class Meta:
        model = Post
        # Incluye todos los campos que el usuario puede subir: texto, imagen y archivo.
        fields = ['contenido', 'imagen', 'archivo']
        
        widgets = {
            'contenido': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': '¿Qué estás pensando? Comparte algo con tu clase...'
            }),
            # FileInput es esencial para el manejo de la subida de archivos (request.FILES)
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
            'archivo': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_contenido(self):
        """
        Aplica la validación de contenido seguro al campo 'contenido'.
        """
        contenido = self.cleaned_data.get('contenido')
        
        # Opcional: Permitir contenido vacío si solo se sube una imagen/archivo
        if contenido:
             return self.validar_contenido_seguro(contenido, 'Publicación')
        
        return contenido

class CommentForm(forms.ModelForm, ContentSecurityMixin):
    class Meta:
        model = Comment
        fields = ['contenido']
        widgets = {
            'contenido': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 1, 
                'placeholder': 'Escribe un comentario...'
            }),
        }

    def clean_contenido(self):
        return self.validar_contenido_seguro(self.cleaned_data.get('contenido'), 'Comentario')

# 🔥 FORMULARIO PARA CREAR/EDITAR GRUPOS (CORREGIDO PARA USAR CAMPOS EN INGLÉS)
class SocialGroupForm(forms.ModelForm):
    class Meta:
        model = SocialGroup
        # 🔥 CLAVE: Los nombres aquí deben ser EXACTAMENTE los del modelo (en inglés)
        fields = ['name', 'description', 'image', 'tipo_privacidad']
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej: Club de Matemáticas'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': '¿Cuál es el propósito de este grupo?'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'tipo_privacidad': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        
        # Etiquetas en español para que el usuario entienda
        labels = {
            'name': 'Nombre del Grupo',
            'description': 'Descripción',
            'image': 'Imagen de Portada',
            'tipo_privacidad': 'Privacidad del Grupo'
        }

# ===================================================================
# 📝 FORMULARIOS DE EDICIÓN DE PERFIL (Para views.editar_perfil)
# ===================================================================

class UserEditForm(forms.ModelForm):
    """Formulario para editar campos del modelo User."""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class PerfilEditForm(forms.ModelForm):
    """Formulario para editar campos del modelo Perfil."""
    class Meta:
        model = Perfil
        fields = ['foto_perfil', 'rol'] 
        widgets = {
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-select', 'disabled': 'disabled'}),
        }

# En tasks/forms.py

class UserEditForm(forms.ModelForm):
    """
    Permite editar los datos básicos de la cuenta (Modelo User).
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu apellido'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@correo.com'}),
        }

# ======================================================
# 2. FORMULARIO DE PERFIL (Fotos, Hobbies, Listas)
# ======================================================
class EditarPerfilForm(forms.ModelForm):
    """
    Formulario COMPLETO para editar el perfil social.
    Se usan 'Textarea' en los campos de gustos para permitir 
    múltiples respuestas (listas verticales).
    """
    class Meta:
        model = Perfil
        fields = [
            'foto_portada', 
            'foto_perfil', 
            'biografia', 
            'hobbies', 
            'gustos_musicales', 
            'libros_favoritos', 
            'materia_favorita', 
            'metas_anio'
        ]
        
        widgets = {
            # --- Entradas de Archivos (Fotos) ---
            'foto_portada': forms.FileInput(attrs={'class': 'form-control'}),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control'}),
            
            # --- Áreas de Texto (Permiten Listas con Enter) ---
            'biografia': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Cuéntanos un poco sobre ti...'
            }),
            
            'hobbies': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Ej:\n- Fútbol\n- Pintura\n- Programación'
            }),
            
            # 🔥 Antes era TextInput, ahora es Textarea para permitir listas
            'gustos_musicales': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Ej:\n- Rock\n- Pop\n- Salsa'
            }),
            
            'libros_favoritos': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Ej:\n- Cien años de soledad\n- Harry Potter'
            }),
            
            # 🔥 Antes era TextInput, ahora es Textarea
            'materia_favorita': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2, 
                'placeholder': 'Ej:\n- Matemáticas\n- Historia'
            }),
            
            'metas_anio': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Ej:\n- Mejorar mi inglés\n- Aprobar todo con superior'
            }),
        }
        
# ===================================================================
# FORMULARIOS ADMINISTRATIVOS (INTACTOS)
# ===================================================================

class BulkCSVForm(forms.Form):
    """
    Formulario para la subida de un archivo CSV en el panel de administración.
    """
    csv_file = forms.FileField(
        label="Seleccionar archivo CSV",
        help_text="Columnas requeridas: first_name, last_name, email, grado, acudiente_first_name, acudiente_last_name, acudiente_email, acudiente_cedula."
    )
    
    anio_escolar = forms.CharField(
        label="Año Escolar",
        max_length=9,
        required=False,
        help_text="Ej: 2025-2026. Si se deja en blanco, se usará el año actual.",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )


class PasswordChangeFirstLoginForm(forms.Form):
    """
    Formulario específico para el cambio de contraseña obligatorio.
    """
    nueva = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput,
        help_text="La contraseña debe tener al menos 8 caracteres."
    )
    confirmar = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        nueva = cleaned_data.get("nueva")
        confirmar = cleaned_data.get("confirmar")

        if nueva and confirmar and nueva != confirmar:
            self.add_error('confirmar', "Las contraseñas no coinciden.")
        
        if nueva and self.user:
            try:
                validate_password(nueva, self.user)
            except ValidationError as e:
                self.add_error('nueva', e)
                
        return cleaned_data

    def save(self, commit=True):
        new_password = self.cleaned_data["nueva"]
        self.user.set_password(new_password)
        if commit:
            self.user.save()
        return self.user

class ProfileSearchForm(forms.Form):
    """
    Formulario para la búsqueda y filtrado de usuarios en el panel.
    """
    query = forms.CharField(
        required=False, 
        label="Buscar",
        widget=forms.TextInput(attrs={'placeholder': 'Usuario, nombre o apellido...'})
    )
    rol = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos los roles')] + [r for r in ROLES_CHOICES if r[0] != 'DIRECTOR_CURSO'],
        label="Filtrar por rol"
    )

# ===================================================================
# FORMULARIO DE OBSERVADOR (LÓGICA ORIGINAL + SEGURIDAD)
# ===================================================================

class ObservacionForm(forms.ModelForm, ContentSecurityMixin):
    class Meta:
        model = Observacion
        fields = ['tipo', 'periodo', 'descripcion', 'compromisos_estudiante', 'compromisos_familia']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'periodo': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detalle la situación...'}),
            'compromisos_estudiante': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Compromisos del estudiante...'}),
            'compromisos_familia': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Compromisos del acudiente...'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None) 
        self.estudiante = kwargs.pop('estudiante', None) 
        super().__init__(*args, **kwargs)

        # Lógica de periodos original intacta
        periodos_qs = Periodo.objects.none()
        
        if self.estudiante:
            matricula = Matricula.objects.filter(estudiante=self.estudiante, activo=True).first()
            if matricula and matricula.curso:
                periodos_qs = Periodo.objects.filter(curso=matricula.curso, activo=True).order_by('id')

        if not periodos_qs.exists():
            primer_curso = Curso.objects.filter(activo=True).first()
            if primer_curso:
                periodos_qs = Periodo.objects.filter(curso=primer_curso, activo=True).order_by('id')
            else:
                periodos_qs = Periodo.objects.filter(activo=True).order_by('id')

        self.fields['periodo'].queryset = periodos_qs
        self.fields['periodo'].label_from_instance = lambda obj: obj.nombre

        if self.instance.pk and not self.instance.es_editable:
            for field in self.fields:
                self.fields[field].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        comp_est = cleaned_data.get('compromisos_estudiante')
        descripcion = cleaned_data.get('descripcion')
        comp_fam = cleaned_data.get('compromisos_familia')

        # 1. Regla de negocio original
        if tipo in ['CONVIVENCIA', 'ACADEMICA'] and not comp_est:
            self.add_error('compromisos_estudiante', 'Para este tipo de observación, el compromiso del estudiante es obligatorio.')

        # 2. 🛡️ Nueva validación de seguridad
        if descripcion:
            self.validar_contenido_seguro(descripcion, 'Descripción')
        if comp_est:
            self.validar_contenido_seguro(comp_est, 'Compromisos Estudiante')
        if comp_fam:
            self.validar_contenido_seguro(comp_fam, 'Compromisos Familia')

        return cleaned_data

# ===================================================================
# FORMULARIO DE MENSAJERÍA INTELIGENTE (LÓGICA ORIGINAL + SEGURIDAD)
# ===================================================================

class MensajeForm(forms.ModelForm, ContentSecurityMixin):
    """
    Formulario profesional con agrupación de destinatarios y soporte de archivos,
    incluyendo opciones para envío masivo por Rol o Curso.
    """
    
    destinatario_rol_masivo = forms.ChoiceField(
        required=False,
        label="Enviar a Rol (Todo el Colegio)",
        choices=[('', '--- Ninguno ---')], # Inicializado con placeholder
        widget=forms.Select(attrs={'class': 'form-select select2-masivo', 'style': 'width: 100%;'})
    )

    destinatario_curso_masivo = forms.ChoiceField(
        required=False,
        label="Enviar a Curso Completo",
        choices=[('', '--- Ninguno ---')], # Inicializado con placeholder
        widget=forms.Select(attrs={'class': 'form-select select2-masivo', 'style': 'width: 100%;'})
    )

    class Meta:
        model = MensajeInterno
        fields = ['destinatario', 'asunto', 'cuerpo', 'archivo']
        widgets = {
            'destinatario': forms.Select(attrs={'class': 'form-select select2', 'style': 'width: 100%;'}),
            'asunto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Asunto del mensaje'}),
            'cuerpo': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Escribe tu mensaje cordial y profesional aquí...'}),
            'archivo': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        # 1. Poblar destinatario individual (Tu lógica existente)
        self.fields['destinatario'].choices = self.get_grouped_destinatarios(user)
        
        # 🔥 CORRECCIÓN CLAVE: Permitir que destinatario (ModelChoiceField) sea opcional
        self.fields['destinatario'].required = False 

        # 2. Poblar destinatarios masivos (NUEVA LÓGICA)
        self.fields['destinatario_rol_masivo'].choices = self.get_roles_masivos(user)
        self.fields['destinatario_curso_masivo'].choices = self.get_cursos_masivos(user)


    def get_roles_masivos(self, user):
        """Define qué roles se pueden seleccionar para envío masivo."""
        ROLES_MASIVOS_CHOICES = [('', '--- Ninguno ---')]
        rol = user.perfil.rol if hasattr(user, 'perfil') else None

        if rol in ['ADMINISTRADOR', 'COORD_ACADEMICO', 'COORD_CONVIVENCIA', 'PSICOLOGO']:
            ROLES_MASIVOS_CHOICES.extend([
                ('ALL_DOCENTES', 'Todo el Cuerpo Docente'),
                ('ALL_ESTUDIANTES', 'Todos los Estudiantes'),
                ('ALL_ACUDIENTES', 'Todos los Acudientes'),
                ('ALL_STAFF', 'Todo el Staff (Coordinación, Psicólogos, Adm.)'),
            ])
        
        if rol == 'DOCENTE':
            ROLES_MASIVOS_CHOICES.append(('MIS_ESTUDIANTES', 'Todos mis Estudiantes Asignados'))
            ROLES_MASIVOS_CHOICES.append(('MIS_ACUDIENTES', 'Todos mis Acudientes Asignados'))

        return ROLES_MASIVOS_CHOICES

    def get_cursos_masivos(self, user):
        """Define qué cursos se pueden seleccionar para envío masivo."""
        CURSO_CHOICES = [('', '--- Ninguno ---')]
        
        # Lógica para obtener cursos: solo para DOCENTES/COORDINADORES/ADMINS
        rol = user.perfil.rol if hasattr(user, 'perfil') else None
        cursos_disponibles = []

        if rol in ['ADMINISTRADOR', 'COORD_ACADEMICO', 'COORD_CONVIVENCIA', 'PSICOLOGO']:
            cursos_disponibles = Curso.objects.filter(activo=True).order_by('grado', 'seccion')
        elif rol == 'DOCENTE':
            mis_cursos_ids = AsignacionMateria.objects.filter(docente=user, activo=True).values_list('curso_id', flat=True).distinct()
            cursos_disponibles = Curso.objects.filter(id__in=mis_cursos_ids).order_by('grado', 'seccion')

        for curso in cursos_disponibles:
            CURSO_CHOICES.append((str(curso.id), f"Curso: {curso.nombre}"))
            
        return CURSO_CHOICES

    # 🛡️ Validaciones de Seguridad Inyectadas
    def clean_asunto(self):
        return self.validar_contenido_seguro(self.cleaned_data.get('asunto'), 'Asunto')

    def clean_cuerpo(self):
        return self.validar_contenido_seguro(self.cleaned_data.get('cuerpo'), 'Mensaje')

    def clean(self):
        cleaned_data = super().clean()
        destinatario_obj = cleaned_data.get('destinatario')
        rol_masivo = cleaned_data.get('destinatario_rol_masivo')
        curso_masivo = cleaned_data.get('destinatario_curso_masivo')

        # Contar cuántos campos tienen valor.
        destinos_seleccionados = []
        if destinatario_obj:
            destinos_seleccionados.append(destinatario_obj)
        if rol_masivo and rol_masivo != '':
            destinos_seleccionados.append(rol_masivo)
        if curso_masivo and curso_masivo != '':
            destinos_seleccionados.append(curso_masivo)

        if len(destinos_seleccionados) > 1:
            raise ValidationError("Solo puedes seleccionar un tipo de destinatario a la vez (Individual, Rol Masivo o Curso Masivo).")
        
        if not destinos_seleccionados:
             raise ValidationError("Debes seleccionar un destinatario individual, un rol masivo o un curso masivo.")
        
        return cleaned_data
        
    def get_grouped_destinatarios(self, user):
        User = get_user_model()
        perfil = getattr(user, 'perfil', None)
        rol = perfil.rol if perfil else None
        
        grupos = [] 
        
        staff_qs = User.objects.filter(
            Q(perfil__rol__in=['ADMINISTRADOR', 'COORD_ACADEMICO', 'COORD_CONVIVENCIA', 'PSICOLOGO'])
        ).exclude(id=user.id).order_by('perfil__rol', 'last_name')
        
        if staff_qs.exists():
            lista_staff = []
            for u in staff_qs:
                cargo = u.perfil.get_rol_display() if hasattr(u, 'perfil') else "Staff"
                lista_staff.append((u.id, f"{cargo}: {u.get_full_name()}"))
            grupos.append(('Directivos y Soporte Técnico', lista_staff))

        if rol in ['ADMINISTRADOR', 'COORD_ACADEMICO', 'COORD_CONVIVENCIA', 'PSICOLOGO']:
            docentes = User.objects.filter(perfil__rol='DOCENTE').exclude(id=user.id).order_by('last_name')
            if docentes.exists():
                grupos.append(('Cuerpo Docente', [(u.id, f"👨‍🏫 {u.get_full_name()}") for u in docentes]))

            todos_cursos = Curso.objects.filter(activo=True).order_by('grado', 'seccion')
            for curso in todos_cursos:
                matriculas = Matricula.objects.filter(curso=curso, activo=True).select_related('estudiante', 'estudiante__perfil')
                lista_alumnos = []
                for mat in matriculas:
                    est = mat.estudiante
                    vinculo = Acudiente.objects.filter(estudiante=est).select_related('acudiente').first()
                    nombre_acudiente = vinculo.acudiente.get_full_name() if vinculo else "Sin acudiente"
                    label = f"🎓 {est.last_name} {est.first_name} (Acudiente: {nombre_acudiente})"
                    lista_alumnos.append((est.id, label))
                if lista_alumnos:
                    grupos.append((f"Curso {curso.nombre}", lista_alumnos))

            acudientes_qs = User.objects.filter(perfil__rol='ACUDIENTE').order_by('last_name')
            if acudientes_qs.exists():
                lista_padres = [(u.id, f"👪 {u.get_full_name()}") for u in acudientes_qs]
                grupos.append(('Todos los Acudientes', lista_padres))

        elif rol == 'DOCENTE':
            colegas = User.objects.filter(perfil__rol='DOCENTE').exclude(id=user.id).order_by('last_name')
            if colegas.exists():
                 grupos.append(('Colegas Docentes', [(u.id, f"👨‍🏫 {u.get_full_name()}") for u in colegas]))
            
            mis_cursos_ids = AsignacionMateria.objects.filter(docente=user, activo=True).values_list('curso_id', flat=True).distinct()
            mis_cursos = Curso.objects.filter(id__in=mis_cursos_ids).order_by('grado', 'seccion')

            for curso in mis_cursos:
                matriculas = Matricula.objects.filter(curso=curso, activo=True).select_related('estudiante')
                lista_alumnos = []
                for m in matriculas:
                    est = m.estudiante
                    vinculo = Acudiente.objects.filter(estudiante=est).select_related('acudiente').first()
                    nombre_acudiente = vinculo.acudiente.get_full_name() if vinculo else "Sin acudiente"
                    label = f"🎓 {est.last_name} {est.first_name} (Acudiente: {nombre_acudiente})"
                    lista_alumnos.append((est.id, label))
                if lista_alumnos:
                    grupos.append((f"Curso {curso.nombre}", lista_alumnos))

        elif rol in ['ESTUDIANTE', 'ACUDIENTE']:
            if rol == 'ESTUDIANTE':
                estudiante_obj = user
            else:
                v = Acudiente.objects.filter(acudiente=user).first()
                estudiante_obj = v.estudiante if v else None
            
            if estudiante_obj:
                mat = Matricula.objects.filter(estudiante=estudiante_obj, activo=True).first()
                if mat and mat.curso:
                    asignaciones = AsignacionMateria.objects.filter(curso=mat.curso, activo=True).select_related('docente', 'materia')
                    lista_profes = []
                    seen_profes = set()
                    for asig in asignaciones:
                        if asig.docente.id not in seen_profes:
                            label = f"👨‍🏫 Prof. {asig.docente.get_full_name()} ({asig.materia.nombre})"
                            lista_profes.append((asig.docente.id, label))
                            seen_profes.add(asig.docente.id)
                    if lista_profes:
                        grupos.append(('Mis Profesores', lista_profes))

        grupos.insert(0, ('', 'Seleccione un destinatario...'))
        return grupos

# ===================================================================
# FORMULARIO DE SEGUIMIENTO (Añadir al final de tasks/forms.py)
# ===================================================================

class SeguimientoForm(forms.ModelForm, ContentSecurityMixin):
    class Meta:
        model = Seguimiento
        fields = ['tipo', 'descripcion', 'observaciones_adicionales'] # Aquí incluimos el campo nuevo
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'II. DETALLE DE LA OBSERVACIÓN, DESCARGOS Y COMPROMISOS...'
            }),
            # Este es el nuevo campo visual:
            'observaciones_adicionales': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'III. OBSERVACIONES ADICIONALES / COMPROMISOS FINALES...'
            }),
        }
        labels = {
            'observaciones_adicionales': 'III. OBSERVACIONES ADICIONALES / COMPROMISOS FINALES'
        }

    # Validaciones de seguridad para evitar groserías en los campos
    def clean_descripcion(self):
        return self.validar_contenido_seguro(self.cleaned_data.get('descripcion'), 'Detalle')

    def clean_observaciones_adicionales(self):
        return self.validar_contenido_seguro(self.cleaned_data.get('observaciones_adicionales'), 'Observaciones Adicionales')


# tasks/forms.py

class ActaInstitucionalForm(forms.ModelForm):
    class Meta:
        model = ActaInstitucional
        fields = [
            'titulo', 'tipo', 'implicado', 
            'lugar', 'fecha', 'hora_fin', 
            'participantes', 'asistentes_externos', 
            'orden_dia', 'contenido', 'compromisos', 
            'archivo_adjunto'
        ]
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            
            'contenido': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'compromisos': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'orden_dia': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Puntos a tratar...'}),
            
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'lugar': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select', 'id': 'tipoSelector'}),
            'asistentes_externos': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # === MAGIA PRO: AGRUPAR USUARIOS POR ROL ===
        User = get_user_model()
        
        # Traemos usuarios activos ordenados por nombre
        users = User.objects.select_related('perfil').filter(is_active=True).order_by('first_name', 'last_name')
        
        # Listas para los grupos
        docentes = []
        directivos = []
        estudiantes = []
        acudientes = []
        otros = []

        for u in users:
            nombre_mostrar = f"{u.get_full_name()} ({u.username})"
            user_id = u.id
            
            try:
                rol = u.perfil.rol
                if rol in ['DOCENTE', 'DIRECTOR_CURSO']:
                    docentes.append((user_id, nombre_mostrar))
                elif rol in ['RECTOR', 'COORDINADOR', 'PSICOLOGO', 'ADMINISTRADOR', 'COORD_CONVIVENCIA', 'COORD_ACADEMICO']:
                    directivos.append((user_id, nombre_mostrar))
                elif rol == 'ESTUDIANTE':
                    estudiantes.append((user_id, nombre_mostrar))
                elif rol == 'ACUDIENTE':
                    acudientes.append((user_id, nombre_mostrar))
                else:
                    otros.append((user_id, nombre_mostrar))
            except:
                otros.append((user_id, nombre_mostrar))

        grupos_usuarios = [
            ('Estudiantes (Prioritario para Descargos)', estudiantes),
            ('Directivos y Staff', directivos),
            ('Docentes', docentes),
            ('Acudientes / Padres', acudientes),
            ('Otros', otros),
        ]
        
        # ✅ CORRECCIÓN 1: Opción vacía por defecto para que no seleccione a nadie automáticamente
        opciones_con_vacio = [('', '--- Ninguno / No Aplica ---')] + grupos_usuarios

        # Asignamos las opciones
        self.fields['participantes'].choices = grupos_usuarios
        self.fields['implicado'].choices = opciones_con_vacio
        
        # ✅ CORRECCIÓN 2: El campo Implicado NO es obligatorio
        self.fields['implicado'].required = False 
        
        # Clases CSS para Select2
        self.fields['participantes'].widget.attrs.update({'class': 'select2-user-search form-control'})
        self.fields['implicado'].widget.attrs.update({
            'class': 'select2-user-search form-control',
            'data-placeholder': 'Buscar persona citada (Solo si aplica)...'
        })
##SMS 

class TelefonoAcudienteForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['telefono_sms', 'recibir_sms']
        labels = {
            'telefono_sms': 'Número de Celular (Colombia)',
            'recibir_sms': 'Autorización de Comunicaciones',
        }
        help_texts = {
            'recibir_sms': 'Autorizo expresamente el envío de notificaciones SMS relacionadas con el desempeño académico, asistencia y novedades urgentes del estudiante a mi cargo.',
        }
        widgets = {
            'telefono_sms': forms.TextInput(attrs={
                'placeholder': 'Ej: 3001234567',
                'class': 'form-control',
                'pattern': '[0-9]{10}'
            }),
            'recibir_sms': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'style': 'cursor: pointer;'
            })
        }

def sanitize_text_input(raw_value: str, max_chars: int) -> str:
    """
    Saneamiento de texto O(N) a nivel de bajo nivel:
    1. Normalización Unicode canónica NFKC (desactiva homógrafos y zero-width bypasses).
    2. Eliminación de Null Bytes (\x00) para evitar truncamiento en bindings de libpq (C).
    3. Strip tags para neutralizar vectores XSS almacenados.
    4. Limpieza de caracteres de control ASCII (0x00 - 0x1F, excepto saltos de línea permitidos).
    """
    if not raw_value:
        return ""

    # Normalización canónica (CPython C-speed)
    normalized = unicodedata.normalize('NFKC', str(raw_value))

    # Eliminación de Null-bytes críticos
    sanitized = normalized.replace('\x00', '')

    # Eliminación estricta de tags HTML
    sanitized = strip_tags(sanitized)

    # Filtrar caracteres de control maliciosos conservando saltos de línea estándar
    sanitized = "".join(
        ch for ch in sanitized
        if ch in ('\n', '\r') or not unicodedata.category(ch).startswith('C')
    )

    return sanitized.strip()[:max_chars]


class SimulatorForm(forms.ModelForm):
    """
    Formulario de alto rendimiento y defensa en profundidad.
    Garantiza integridad de datos, saneamiento de strings contra ataques de inyección,
    validación de colisiones de URL idempotente y atributos semánticos para WCAG 2.1 AA.
    """

    class Meta:
        model = Simulator
        fields = ['title', 'subject', 'description', 'url', 'order', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control rounded-3 shadow-none',
                'placeholder': 'Ej. 2.2 Estructura subatómica: Protones y Neutrones',
                'autocomplete': 'off',
                'maxlength': '200',
                'aria-required': 'true',
                'aria-label': 'Título del simulador',
                'spellcheck': 'true',
            }),
            'subject': forms.Select(attrs={
                'class': 'form-select rounded-3 shadow-none',
                'aria-required': 'true',
                'aria-label': 'Materia o disciplina académica',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control rounded-3 shadow-none',
                'rows': 3,
                'placeholder': 'Descripción didáctica y objetivos de aprendizaje del applet...',
                'maxlength': '1500',
                'aria-required': 'true',
                'aria-label': 'Descripción pedagógica',
                'spellcheck': 'true',
            }),
            'url': forms.URLInput(attrs={
                'class': 'form-control rounded-3 shadow-none font-monospace',
                'placeholder': 'https://ai.studio/apps/...',
                'autocomplete': 'off',
                'autocapitalize': 'none',
                'inputmode': 'url',
                'spellcheck': 'false',
                'aria-required': 'true',
                'aria-label': 'URL segura HTTPS del simulador',
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control rounded-3 shadow-none font-monospace',
                'min': '0',
                'max': '32767',
                'placeholder': '0',
                'inputmode': 'numeric',
                'aria-label': 'Orden secuencial de aparición',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input ms-2 cursor-pointer',
                'role': 'switch',
                'aria-label': 'Activar visibilidad para estudiantes',
            }),
        }

    def clean_title(self) -> str:
        raw_title = self.cleaned_data.get('title', '')
        clean_title = sanitize_text_input(raw_title, max_chars=200)

        if len(clean_title) < 3:
            raise ValidationError(
                _("El título debe contener al menos 3 caracteres alfanuméricos válidos."),
                code='title_too_short'
            )
        return clean_title

    def clean_description(self) -> str:
        raw_desc = self.cleaned_data.get('description', '')
        clean_desc = sanitize_text_input(raw_desc, max_chars=1500)

        if len(clean_desc) < 5:
            raise ValidationError(
                _("La descripción didáctica debe contener al menos 5 caracteres descriptivos."),
                code='description_too_short'
            )
        return clean_desc

    def clean_url(self) -> str:
        raw_url = self.cleaned_data.get('url', '').strip()

        # Validación anti-CRLF (bloquea inyecciones de cabecera HTTP en proxies)
        if any(c in raw_url for c in ('\r', '\n', '\t', '\x00')):
            raise ValidationError(
                _("La URL contiene caracteres de control o saltos de línea prohibidos."),
                code='crlf_detected'
            )

        parsed = urlparse(raw_url)
        if parsed.scheme.lower() != 'https':
            raise ValidationError(
                _("Protocolo inseguro. Solo se permiten recursos bajo HTTPS estricto."),
                code='insecure_scheme'
            )

        if not parsed.netloc:
            raise ValidationError(
                _("La URL carece de un Fully Qualified Domain Name (FQDN) válido."),
                code='invalid_fqdn'
            )

        # Validación de idempotencia / colisión de URL en base de datos
        query = Simulator.objects.filter(url=raw_url)
        if self.instance and self.instance.pk:
            query = query.exclude(pk=self.instance.pk)

        if query.exists():
            raise ValidationError(
                _("Ya existe un simulador registrado con esta misma URL."),
                code='duplicate_url'
            )

        return raw_url

    def clean_order(self) -> int:
        order = self.cleaned_data.get('order')
        if order is None or order < 0:
            return 0
        if order > 32767:
            raise ValidationError(
                _("El valor de orden excede el límite permitido de base de datos (SmallInt: 32767)."),
                code='order_overflow'
            )
        return order





class MasterClassForm(forms.ModelForm):
    class Meta:
        model = MasterClass
        fields = [
            'title',
            'subject',
            'description',
            'video_url',
            'duration_minutes',
            'order',
            'is_active',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control rounded-3',
                'placeholder': 'Ej. 1.3 Propiedades de la materia: Físicas y Químicas'
            }),
            'subject': forms.Select(attrs={
                'class': 'form-select rounded-3'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control rounded-3',
                'rows': 3,
                'placeholder': 'Sintetiza los objetivos conceptuales y competencias clave...'
            }),
            'video_url': forms.URLInput(attrs={
                'class': 'form-control rounded-3',
                'placeholder': 'https://pub-46cdb180c9f64bb48ed13753c8e88943.r2.dev/...'
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control rounded-3',
                'min': 1
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control rounded-3',
                'min': 1
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input ms-2'
            }),
        }

    def clean_video_url(self):
        url = self.cleaned_data.get('video_url', '').strip()
        if not url.startswith('https://'):
            raise forms.ValidationError("Por políticas de AppSec, el video debe servirse estrictamente vía HTTPS.")
        return url


class MasterClassForm(forms.ModelForm):
    class Meta:
        model = MasterClass
        fields = ['title', 'subject', 'order', 'video_url', 'duration_minutes', 'description', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control bg-dark text-white border-secondary rounded-3 font-monospace',
                'placeholder': 'Ej: 2.5 Arquitectura de la Tabla Periódica'
            }),
            'subject': forms.Select(attrs={
                'class': 'form-select bg-dark text-white border-secondary rounded-3 font-monospace'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control bg-dark text-white border-secondary rounded-3 font-monospace',
                'placeholder': '1, 2, 3...'
            }),
            'video_url': forms.URLInput(attrs={
                'class': 'form-control bg-dark text-white border-secondary rounded-3 font-monospace',
                'placeholder': 'https://pub-xxxxxx.r2.dev/clase_quimica_01.mp4'
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control bg-dark text-white border-secondary rounded-3 font-monospace',
                'placeholder': '45'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control bg-dark text-white border-secondary rounded-3 font-monospace',
                'rows': 3,
                'placeholder': 'Descripción pedagógica, objetivos de aprendizaje y conceptos clave...'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input bg-dark border-secondary'
            }),
        }