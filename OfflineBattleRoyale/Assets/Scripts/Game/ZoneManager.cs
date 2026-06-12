using System;
using UnityEngine;

public class ZoneManager : MonoBehaviour
{
  public static ZoneManager Instance { get; private set; }

  [SerializeField] private Transform safeZoneCircle;
  [SerializeField] private float initialRadius = 400f;
  [SerializeField] private float shrinkScaleFactor = 0.75f;
  [SerializeField] private float shrinkInterval = 45f;
  [SerializeField] private float firstShrinkDelay = 60f;
  [SerializeField] private float centerShiftRange = 10f;
  [SerializeField] private float outsideDamagePerSecond = 8f;

  private float currentRadius;
  private float nextShrinkTime;

  public float CurrentRadius => currentRadius;
  public Vector3 SafeZoneCenter => safeZoneCircle != null ? safeZoneCircle.position : Vector3.zero;
  public float OutsideDamagePerSecond => outsideDamagePerSecond;

  public event Action OnZoneShrunk;

  private void Awake()
  {
    if (Instance != null && Instance != this)
    {
      Destroy(gameObject);
      return;
    }

    Instance = this;
    currentRadius = initialRadius;

    if (safeZoneCircle != null)
    {
      safeZoneCircle.localScale = Vector3.one * (initialRadius * 2f);
    }
  }

  private void Start()
  {
    nextShrinkTime = Time.time + firstShrinkDelay;
  }

  private void Update()
  {
    if (Time.time >= nextShrinkTime)
    {
      ShrinkPlayZone();
      nextShrinkTime = Time.time + shrinkInterval;
    }
  }

  public void ShrinkPlayZone()
  {
    currentRadius *= shrinkScaleFactor;

    if (safeZoneCircle != null)
    {
      safeZoneCircle.localScale *= shrinkScaleFactor;
      safeZoneCircle.position += new Vector3(
        UnityEngine.Random.Range(-centerShiftRange, centerShiftRange),
        0f,
        UnityEngine.Random.Range(-centerShiftRange, centerShiftRange)
      );
    }

    OnZoneShrunk?.Invoke();
  }

  public bool IsInsideSafeZone(Vector3 position)
  {
    Vector3 flatPosition = new Vector3(position.x, SafeZoneCenter.y, position.z);
    float distance = Vector3.Distance(flatPosition, SafeZoneCenter);
    return distance <= currentRadius;
  }

  public Vector3 GetSafeZoneCenter()
  {
    return SafeZoneCenter;
  }

  public float GetDistanceOutsideZone(Vector3 position)
  {
    Vector3 flatPosition = new Vector3(position.x, SafeZoneCenter.y, position.z);
    return Mathf.Max(0f, Vector3.Distance(flatPosition, SafeZoneCenter) - currentRadius);
  }
}
