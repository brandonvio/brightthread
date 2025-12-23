document.addEventListener("DOMContentLoaded", function() {
  // Initialize mermaid first with startOnLoad disabled
  mermaid.initialize({
    startOnLoad: false,
    theme: 'dark',
    themeVariables: {
      primaryColor: '#5D8AA8',
      primaryTextColor: '#fff',
      primaryBorderColor: '#7C93C3',
      lineColor: '#8FBCBB',
      secondaryColor: '#4C566A',
      tertiaryColor: '#3B4252',
      background: '#2E3440'
    }
  });

  // Find all code blocks with language-mermaid class and convert them
  document.querySelectorAll('pre code.language-mermaid').forEach(function(codeBlock) {
    var pre = codeBlock.parentElement;
    var div = document.createElement('div');
    div.className = 'mermaid';
    div.textContent = codeBlock.textContent;
    pre.parentNode.replaceChild(div, pre);
  });

  // Run mermaid rendering
  mermaid.run();

  // Use MutationObserver to detect when SVGs are rendered, then add click handlers
  var observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      mutation.addedNodes.forEach(function(node) {
        if (node.tagName === 'svg') {
          var parent = node.parentElement;
          if (parent && parent.classList.contains('mermaid') && !parent.hasAttribute('data-lightbox-enabled')) {
            parent.setAttribute('data-lightbox-enabled', 'true');
            parent.style.cursor = 'pointer';
            parent.title = 'Click to zoom';
            parent.addEventListener('click', function() {
              openDiagramLightbox(parent);
            });
          }
        }
      });
    });
  });

  // Observe all mermaid containers for SVG insertion
  document.querySelectorAll('.mermaid').forEach(function(container) {
    observer.observe(container, { childList: true });

    // Also check if SVG is already there (in case mermaid rendered before observer started)
    if (container.querySelector('svg') && !container.hasAttribute('data-lightbox-enabled')) {
      container.setAttribute('data-lightbox-enabled', 'true');
      container.style.cursor = 'pointer';
      container.title = 'Click to zoom';
      container.addEventListener('click', function() {
        openDiagramLightbox(container);
      });
    }
  });
});

// Lightbox with pan/zoom functionality
function openDiagramLightbox(diagramElement) {
  // Create lightbox overlay
  var overlay = document.createElement('div');
  overlay.className = 'mermaid-lightbox-overlay';

  // Create lightbox container
  var lightbox = document.createElement('div');
  lightbox.className = 'mermaid-lightbox';

  // Create controls
  var controls = document.createElement('div');
  controls.className = 'mermaid-lightbox-controls';
  controls.innerHTML =
    '<button class="mermaid-lb-btn" data-action="zoom-in" title="Zoom In">+</button>' +
    '<button class="mermaid-lb-btn" data-action="zoom-out" title="Zoom Out">-</button>' +
    '<button class="mermaid-lb-btn" data-action="reset" title="Reset View">Reset</button>' +
    '<span class="mermaid-lb-hint">Drag to pan, scroll to zoom</span>' +
    '<button class="mermaid-lb-btn mermaid-lb-close" data-action="close" title="Close (Esc)">Close</button>';

  // Create diagram container for pan/zoom
  var contentArea = document.createElement('div');
  contentArea.className = 'mermaid-lightbox-content';

  var innerWrapper = document.createElement('div');
  innerWrapper.className = 'mermaid-lightbox-inner';

  // Clone the SVG
  var svg = diagramElement.querySelector('svg');
  if (!svg) return;

  var clonedSvg = svg.cloneNode(true);

  // Get dimensions from viewBox and set explicit pixel size
  var viewBox = svg.getAttribute('viewBox');
  if (viewBox) {
    var parts = viewBox.split(/[\s,]+/);
    if (parts.length === 4) {
      var vbWidth = parseFloat(parts[2]);
      var vbHeight = parseFloat(parts[3]);
      clonedSvg.setAttribute('width', vbWidth);
      clonedSvg.setAttribute('height', vbHeight);
      clonedSvg.style.width = vbWidth + 'px';
      clonedSvg.style.height = vbHeight + 'px';
    }
  }

  innerWrapper.appendChild(clonedSvg);

  contentArea.appendChild(innerWrapper);
  lightbox.appendChild(controls);
  lightbox.appendChild(contentArea);
  overlay.appendChild(lightbox);
  document.body.appendChild(overlay);
  document.body.style.overflow = 'hidden';

  // Pan/zoom state - start at 100% scale, centered
  var scale = 1;
  var translateX = 0;
  var translateY = 0;
  var isDragging = false;
  var startX, startY;

  function updateTransform() {
    innerWrapper.style.transform = 'translate(' + translateX + 'px, ' + translateY + 'px) scale(' + scale + ')';
  }

  // Initialize centered
  updateTransform();

  // Close handler
  function closeLightbox() {
    document.body.removeChild(overlay);
    document.body.style.overflow = '';
    document.removeEventListener('keydown', keyHandler);
    document.removeEventListener('mousemove', moveHandler);
    document.removeEventListener('mouseup', upHandler);
  }

  // Button click handlers
  controls.addEventListener('click', function(e) {
    var action = e.target.getAttribute('data-action');
    if (action === 'zoom-in') {
      scale = Math.min(scale * 1.25, 10);
      updateTransform();
    } else if (action === 'zoom-out') {
      scale = Math.max(scale / 1.25, 0.1);
      updateTransform();
    } else if (action === 'reset') {
      scale = 1;
      translateX = 0;
      translateY = 0;
      updateTransform();
    } else if (action === 'close') {
      closeLightbox();
    }
  });

  // Click outside to close
  overlay.addEventListener('click', function(e) {
    if (e.target === overlay) {
      closeLightbox();
    }
  });

  // Escape key to close
  function keyHandler(e) {
    if (e.key === 'Escape') {
      closeLightbox();
    }
  }
  document.addEventListener('keydown', keyHandler);

  // Mouse wheel zoom
  contentArea.addEventListener('wheel', function(e) {
    e.preventDefault();
    var delta = e.deltaY > 0 ? 0.9 : 1.1;
    scale = Math.min(Math.max(scale * delta, 0.1), 10);
    updateTransform();
  });

  // Pan with mouse drag
  contentArea.addEventListener('mousedown', function(e) {
    isDragging = true;
    startX = e.clientX - translateX;
    startY = e.clientY - translateY;
    contentArea.style.cursor = 'grabbing';
  });

  function moveHandler(e) {
    if (!isDragging) return;
    translateX = e.clientX - startX;
    translateY = e.clientY - startY;
    updateTransform();
  }
  document.addEventListener('mousemove', moveHandler);

  function upHandler() {
    isDragging = false;
    contentArea.style.cursor = 'grab';
  }
  document.addEventListener('mouseup', upHandler);

  contentArea.style.cursor = 'grab';
}
