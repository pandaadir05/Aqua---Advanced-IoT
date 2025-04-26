"""
Plugin system for extending Aqua functionality.
"""

import importlib
import inspect
import pkgutil
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Type, Callable
from loguru import logger

class AquaPlugin:
    """Base class for all Aqua plugins."""
    
    name = "base_plugin"
    version = "1.0.0"
    description = "Base plugin class"
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the plugin.
        
        Args:
            config: Optional plugin configuration
        """
        self.config = config or {}
        
    def initialize(self) -> bool:
        """
        Initialize the plugin. Called when the plugin is loaded.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        return True
        
    def shutdown(self) -> None:
        """Clean up resources. Called when the plugin is unloaded."""
        pass

class PluginManager:
    """Manager for loading and handling plugins."""
    
    def __init__(self, plugin_dir: str = "plugins"):
        """
        Initialize the plugin manager.
        
        Args:
            plugin_dir: Directory containing plugins
        """
        self.plugin_dir = Path(plugin_dir)
        self.plugins: Dict[str, AquaPlugin] = {}
        self.plugin_classes: Dict[str, Type[AquaPlugin]] = {}
        
        # Create plugin directory if it doesn't exist
        self.plugin_dir.mkdir(exist_ok=True)
        
        # Add plugin directory to Python path
        if str(self.plugin_dir.absolute()) not in sys.path:
            sys.path.insert(0, str(self.plugin_dir.absolute()))
            
    def discover_plugins(self) -> List[str]:
        """
        Discover available plugins.
        
        Returns:
            List of plugin names
        """
        discovered = []
        
        # Look for Python modules in the plugin directory
        for _, name, is_pkg in pkgutil.iter_modules([str(self.plugin_dir)]):
            if not is_pkg:
                try:
                    # Import the module
                    module = importlib.import_module(name)
                    
                    # Find plugin classes
                    for item_name, item in inspect.getmembers(module, inspect.isclass):
                        if issubclass(item, AquaPlugin) and item is not AquaPlugin:
                            self.plugin_classes[item.name] = item
                            discovered.append(item.name)
                            logger.info(f"Discovered plugin: {item.name} ({item.description})")
                except Exception as e:
                    logger.error(f"Error discovering plugin {name}: {e}")
                    
        return discovered
        
    def load_plugin(self, name: str, config: Optional[Dict] = None) -> bool:
        """
        Load a plugin.
        
        Args:
            name: Plugin name
            config: Optional plugin configuration
            
        Returns:
            True if the plugin was loaded successfully, False otherwise
        """
        if name in self.plugins:
            logger.warning(f"Plugin {name} already loaded")
            return True
            
        if name not in self.plugin_classes:
            logger.error(f"Plugin {name} not found")
            return False
            
        try:
            # Instantiate the plugin
            plugin = self.plugin_classes[name](config)
            
            # Initialize the plugin
            if plugin.initialize():
                self.plugins[name] = plugin
                logger.info(f"Plugin {name} loaded successfully")
                return True
            else:
                logger.error(f"Plugin {name} initialization failed")
                return False
        except Exception as e:
            logger.error(f"Error loading plugin {name}: {e}")
            return False
            
    def unload_plugin(self, name: str) -> bool:
        """
        Unload a plugin.
        
        Args:
            name: Plugin name
            
        Returns:
            True if the plugin was unloaded successfully, False otherwise
        """
        if name not in self.plugins:
            logger.warning(f"Plugin {name} not loaded")
            return False
            
        try:
            # Call shutdown method
            self.plugins[name].shutdown()
            
            # Remove from loaded plugins
            del self.plugins[name]
            logger.info(f"Plugin {name} unloaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error unloading plugin {name}: {e}")
            return False
            
    def get_plugin(self, name: str) -> Optional[AquaPlugin]:
        """
        Get a loaded plugin.
        
        Args:
            name: Plugin name
            
        Returns:
            Plugin instance or None if not found
        """
        return self.plugins.get(name)
        
    def list_loaded_plugins(self) -> List[Dict[str, str]]:
        """
        List all loaded plugins.
        
        Returns:
            List of plugin information
        """
        return [
            {
                "name": plugin.name,
                "version": plugin.version,
                "description": plugin.description
            }
            for plugin in self.plugins.values()
        ]
