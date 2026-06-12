using UnityEngine;
using UnityEngine.UI;

public class MinimapController : MonoBehaviour
{
  [SerializeField] private RectTransform playerIcon;
  [SerializeField] private RectTransform zoneIcon;
  [SerializeField] private Transform player;
  [SerializeField] private float mapScale = 0.25f;
  [SerializeField] private Vector2 mapSize = new Vector2(180f, 180f);

  private void Update()
  {
    if (player == null)
    {
      return;
    }

    if (playerIcon != null)
    {
      playerIcon.anchoredPosition = WorldToMinimap(player.position);
    }

    if (zoneIcon != null && ZoneManager.Instance != null)
    {
      zoneIcon.anchoredPosition = WorldToMinimap(ZoneManager.Instance.SafeZoneCenter);
      float zoneDiameter = ZoneManager.Instance.CurrentRadius * 2f * mapScale;
      zoneIcon.sizeDelta = new Vector2(zoneDiameter, zoneDiameter);
    }
  }

  private Vector2 WorldToMinimap(Vector3 worldPosition)
  {
    return new Vector2(worldPosition.x, worldPosition.z) * mapScale;
  }
}
