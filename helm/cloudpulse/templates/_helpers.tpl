{{/* Chart name, trimmed to the 63-char K8s name limit */}}
{{- define "cloudpulse.name" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/* Full resource name; avoids "cloudpulse-cloudpulse" when release name equals chart name */}}
{{- define "cloudpulse.fullname" -}}
{{- if contains .Chart.Name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{/* Selector labels: must stay stable, used to match pods */}}
{{- define "cloudpulse.selectorLabels" -}}
app.kubernetes.io/name: {{ include "cloudpulse.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{/* Common labels added to every resource */}}
{{- define "cloudpulse.labels" -}}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version }}
{{ include "cloudpulse.selectorLabels" . }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: cloudpulse-platform
{{- end -}}

{{/* Image reference; falls back to the chart appVersion when tag is empty */}}
{{- define "cloudpulse.image" -}}
{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}
{{- end -}}
