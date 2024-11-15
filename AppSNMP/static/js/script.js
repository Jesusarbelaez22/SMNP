// Asignar las variables a partir de valores de Flask en el HTML
var timestamps = JSON.parse(document.getElementById('timestamps-data').textContent);
var memory_physical_values = JSON.parse(document.getElementById('memory-physical-values-data').textContent);
var memory_virtual_values = JSON.parse(document.getElementById('memory-virtual-values-data').textContent);

// Verifica si los datos están presentes antes de graficar
if (timestamps.length > 0) {
    // Gráfico de Uso de Memoria Física
    var memoryPhysicalData = [{
        x: timestamps,
        y: memory_physical_values,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Uso de Memoria Física (%)'
    }];
    
    var memoryPhysicalLayout = {
        title: 'Historial de Uso de Memoria Física (Últimos 3 días)',
        xaxis: { title: 'Tiempo' },
        yaxis: { title: 'Uso de Memoria Física (%)' }
    };
    Plotly.newPlot('memory-physical-chart', memoryPhysicalData, memoryPhysicalLayout);

    // Gráfico de Uso de Memoria Virtual
    var memoryVirtualData = [{
        x: timestamps,
        y: memory_virtual_values,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Uso de Memoria Virtual (%)'
    }];
    
    var memoryVirtualLayout = {
        title: 'Historial de Uso de Memoria Virtual (Últimos 3 días)',
        xaxis: { title: 'Tiempo' },
        yaxis: { title: 'Uso de Memoria Virtual (%)' }
    };
    Plotly.newPlot('memory-virtual-chart', memoryVirtualData, memoryVirtualLayout);

} else {
    document.body.innerHTML += "<p>No hay datos disponibles para mostrar.</p>";
}
