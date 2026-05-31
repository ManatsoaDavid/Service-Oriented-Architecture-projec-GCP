{{- define "hotel.name" -}}
{{- .Chart.Name }}
{{- end }}

{{- define "hotel.labels" -}}
app.kubernetes.io/name: {{ include "hotel.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}
