#if UNITY_EDITOR
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

[InitializeOnLoad]
public static class BattleRoyalePlayBootstrap
{
  private const string ScenePath = "Assets/Scenes/BattleRoyaleIsland.unity";

  static BattleRoyalePlayBootstrap()
  {
    EditorApplication.playModeStateChanged += OnPlayModeStateChanged;
  }

  private static void OnPlayModeStateChanged(PlayModeStateChange state)
  {
    if (state != PlayModeStateChange.ExitingEditMode)
    {
      return;
    }

    if (Object.FindFirstObjectByType<GameManager>() != null)
    {
      return;
    }

    bool regenerate = EditorUtility.DisplayDialog(
      "Regenerate Map?",
      "No battle royale scene was found.\n\nClick Regenerate to build the island, buildings, weapons, bots, and UI automatically.",
      "Regenerate",
      "Cancel"
    );

    if (!regenerate)
    {
      EditorApplication.isPlaying = false;
      return;
    }

    BattleRoyaleMapBuilder.RegenerateMap(silent: true);
    EditorSceneManager.OpenScene(ScenePath);
  }
}
#endif
