from django.contrib import admin

from .models import User
from django.contrib import admin
from django.utils.html import format_html
from .models import (Device, AuthorizationToken, Command, ActionParameter)


class DeviceAdmin(admin.ModelAdmin):
    list_display = ('device_id', 'device_type', 'is_active', 'registered_at', 'last_seen')
    list_filter = ('device_type', 'is_active')
    search_fields = ('device_id', 'device_type')
    readonly_fields = ('capabilities_formatted',)

    def capabilities_formatted(self, obj):
        """Format capabilities as badges"""
        if not obj.capabilities:
            return "-"

        html = "<div style='display: flex; flex-wrap: wrap; gap: 5px;'>"
        for capability in obj.capabilities:
            background = "#e0f0ff"  # Default blue

            # Special color for code execution capabilities
            if capability.startswith("execute_code"):
                background = "#ffe0e0"  # Light red

            html += f"<span style='background: {background}; padding: 3px 8px; border-radius: 10px; font-size: 12px;'>{capability}</span>"

        html += "</div>"
        return format_html(html)

    capabilities_formatted.short_description = "Capabilities"


class AuthorizationTokenAdmin(admin.ModelAdmin):
    list_display = ('token', 'created_at', 'expires_at', 'is_used', 'is_valid')
    list_filter = ('is_used',)
    search_fields = ('token',)
    readonly_fields = ('is_valid',)


class CommandAdmin(admin.ModelAdmin):
    list_display = ('name', 'device_info', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'name')
    search_fields = ('name', 'device__device_id')
    readonly_fields = ('result_formatted', 'code_preview', 'input_data_preview')

    def device_info(self, obj):
        return f"{obj.device.device_type} ({obj.device.device_id})"

    def code_preview(self, obj):
        """Show code for code execution commands"""
        if obj.name not in ["execute_code", "execute_code_with_input"] or "code" not in obj.params:
            return "-"

        code = obj.params["code"]
        return format_html(
            "<pre style='background-color: #f5f5f5; padding: 10px; border-radius: 5px; max-height: 300px; overflow: auto;'>{}</pre>",
            code)

    code_preview.short_description = "Code"

    def input_data_preview(self, obj):
        """Show input data for code execution with input commands"""
        if obj.name != "execute_code_with_input" or "input_data" not in obj.params:
            return "-"

        data = obj.params["input_data"]
        return format_html(
            "<pre style='background-color: #f5f5f5; padding: 10px; border-radius: 5px; max-height: 150px; overflow: auto;'>{}</pre>",
            data)

    input_data_preview.short_description = "Input Data"

    def result_formatted(self, obj):
        """Format command result for better readability in admin"""
        if not obj.result:
            return "-"

        # Special handling for code execution results
        if obj.name in ["execute_code", "execute_code_with_input"] and isinstance(obj.result, dict):
            result = obj.result

            # Format the result nicely with colors and proper spacing
            html = "<div style='font-family: monospace;'>"

            # Show execution status with color
            if result.get('status') == 'completed':
                if result.get('result', {}).get('success', False):
                    html += "<div style='color: green; font-weight: bold;'>Execution successful</div>"
                else:
                    html += "<div style='color: orange; font-weight: bold;'>Execution completed with errors</div>"
            else:
                html += f"<div style='color: red; font-weight: bold;'>Status: {result.get('status', 'unknown')}</div>"

            # Show the execution result
            if 'result' in result and isinstance(result['result'], dict):
                code_result = result['result']

                # Show stdout if available
                if 'stdout' in code_result and code_result['stdout']:
                    html += "<div style='margin-top: 10px;'><strong>Standard Output:</strong></div>"
                    html += f"<pre style='background-color: #f5f5f5; padding: 10px; border-radius: 5px;'>{code_result['stdout']}</pre>"

                # Show stderr if available
                if 'stderr' in code_result and code_result['stderr']:
                    html += "<div style='margin-top: 10px;'><strong>Standard Error:</strong></div>"
                    html += f"<pre style='background-color: #fff0f0; padding: 10px; border-radius: 5px;'>{code_result['stderr']}</pre>"

                # Show any errors
                if 'error' in code_result:
                    html += "<div style='margin-top: 10px;'><strong>Error:</strong></div>"
                    html += f"<pre style='background-color: #ffe0e0; padding: 10px; border-radius: 5px;'>{code_result['error_type'] if 'error_type' in code_result else 'Error'}: {code_result['error']}</pre>"

                # Show result value if available
                if 'result' in code_result and code_result['result'] is not None:
                    html += "<div style='margin-top: 10px;'><strong>Return Value:</strong></div>"

                    # Format the result value based on type
                    result_value = code_result['result']
                    if isinstance(result_value, (dict, list)):
                        import json
                        result_str = json.dumps(result_value, indent=2)
                    else:
                        result_str = str(result_value)

                    html += f"<pre style='background-color: #e0f0e0; padding: 10px; border-radius: 5px;'>{result_str}</pre>"

            html += "</div>"
            return format_html(html)

        # Default formatting for other command types
        import json
        formatted_json = json.dumps(obj.result, indent=2)
        return format_html("<pre>{}</pre>", formatted_json)
# Register your models here.
admin.site.register(User)